# Copyright (C) 2012-2013 Pablo Oliveira <pablo@sifflez.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#!/usr/bin/env python
from zipfile import ZipFile
import os
import subprocess
import resource
import json
import shutil
import tempfile
from celery import Celery
from contextlib import closing

from flask import Config

from tigergrader.database import connect_db
from tigergrader.compare import compare

cfg = Config('.')
cfg.from_envvar('TIGERGRADER_SETTINGS')
celery = Celery('grader', backend=cfg["CELERY_BACKEND"],
                broker=cfg["CELERY_BROKER"])


def report_error(msg, *args, **kwargs):
    raise Exception(msg.format(*args, **kwargs) + "\n")


def setlimits():
    resource.setrlimit(resource.RLIMIT_CPU, (cfg["CPU_LIMIT"],
                                             cfg["CPU_LIMIT"]))
    resource.setrlimit(resource.RLIMIT_AS, (cfg["AS_LIMIT"],
                                            cfg["AS_LIMIT"]))


def call(cmd):
    try:
        pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, preexec_fn=setlimits)
        output = pipe.communicate()
        return pipe.returncode, output[0], output[1]
    except OSError as e:
        report_error("Failed executing command {0}\n{1}", " ".join(cmd),
                     str(e))


def unzip(f):
    z = None
    try:
        z = ZipFile(f, 'r')
        # Check that the zip file is conformant
        for n in z.namelist():
            if not n.startswith(cfg["EXPECTED_DIR"]) or ".." in n:
                report_error("Your zip file should contain only"
                             " the {0} directory and cannot contain "
                             " paths like {1}", cfg["EXPECTED_DIR"], n)
        # Extract it
        z.extractall()
    except Exception as e:
        report_error("Could not unzip file: {0}\n{1}", f, str(e))
    finally:
        if z:
            z.close()


def build():
    status, out, err = call([cfg["BUILD_COMMAND"]])
    if status != 0:
        report_error("build failed with the following output:\n{0}\n{1}",
                     err, out)


def write_policy(testfile):
    with file(cfg["POLICY_FILE"], "w") as f:
        f.write(cfg["POLICY"].format(input_file=testfile))


def check(testfile, exp_status, status, out, err):
    res = dict(testfile=testfile, status=status, out=out, err=err,
               exp_out="", exp_err="", exp_status=exp_status)

    check = (exp_status == status)

    err_file = testfile + ".err"
    if os.path.exists(err_file):
        exp_err = file(err_file).read()
        res["exp_err"] = exp_err

        err_check = compare(exp_err, err, strict=False)
        check = check and err_check[0]

    out_file = testfile + ".out"
    if os.path.exists(out_file):
        exp_out = file(out_file).read()
        res["exp_out"] = exp_out

        out_check = compare(exp_out, out, strict=False)
        check = check and out_check[0]

    res["check"] = check

    return res


def run_tests(testdir):
    tests = None
    result = []
    try:
        with file(os.path.join(testdir, "manifest.json")) as f:
            tests = json.load(f)
    except Exception as e:
        report_error("Could not find tests manifest {0}", e)

    jclass = tests["class"]
    topt = tests["opts"]
    total_tests = 0
    passed_tests = 0
    grade = 0.0
    coefs = 0.0
    for test_info in tests["tests"]:
        t = test_info["input"]
        if "exitcode" in test_info:
            exp_status = test_info["exitcode"]
        else:
            exp_status = 0

        print "."
        testfile = os.path.abspath(os.path.join(testdir, t))
        write_policy(testfile)
        status, out, err = call([cfg["RUN_COMMAND"]] + cfg["RUN_OPTS"]
                                + [jclass, topt, testfile])
        rescheck = check(testfile, exp_status, status, out, err)
        result.append(rescheck)
        total_tests += 1

        if "coef" in test_info:
            c = float(test_info["coef"])
        else:
            c = 1.0

        coefs += c

        if rescheck["check"]:
            grade += c
            passed_tests += 1

    return dict(grade=round(grade / coefs * 20), tests=result)


def prepare_env(test):
    tmp_dir = tempfile.mkdtemp()
    test_env = os.path.join(tmp_dir, "sandbox")
    shutil.copytree(os.path.join(cfg["SANDBOX_BLUEPRINT"], test), test_env)
    os.chdir(test_env)
    return tmp_dir


def store(result, test, user, zipf):
    with closing(connect_db()) as db:
        c = db.cursor()
        print "Insert into database"
        c.execute("INSERT INTO reports VALUES(?,?)",
                  (None, json.dumps(result["tests"])))
        report_id = c.lastrowid

        c.execute("INSERT INTO grades VALUES(?,?,?,?,?,current_timestamp)",
                  (user,
                   test,
                   result["grade"],
                   report_id,
                   os.path.basename(zipf)))
        db.commit()


@celery.task
def grade(zipf, test, user=None):
    testdir = os.path.join(cfg["MODULE_FOLDER"], test)
    if not os.path.exists(zipf):
        report_error("Zipfile was not uploaded")
    if not os.path.exists(testdir):
        report_error("Test {0} does not exists", test)
    if not (os.path.isabs(zipf)):
        report_error("Internal error. Path must be absolute")
    old_path = os.getcwd()
    tmp_dir = None
    try:
        tmp_dir = prepare_env(test)
        print "z"
        unzip(zipf)
        print "b"
        build()
        print "t"
        result = run_tests(testdir)
        store(result, test, user, zipf)
        return result
    except Exception as e:
        result = {"tests": [{"error": str(e)}], "grade": -1}
        store(result, test, user, zipf)
        return result
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir)
        os.chdir(old_path)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Test student's submitted code")
    parser.add_argument('source', metavar='source.zip',
                        help='A zip file')
    parser.add_argument('testdir',
                        help='A directory containing the input tests')
    parser.add_argument('results',
                        help='Path where results will be written')

    args = parser.parse_args()
    result = grade(args.source, args.testdir)
    with file(args.results, "w") as f:
        json.dump(result, f, indent=2)
