import os
import json
import shutil
from contextlib import closing
from database import connect_db
from zipfile import ZipFile
from tempfile import mkdtemp
from subprocess import check_output, STDOUT, CalledProcessError
from flask import Config

cfg = Config('.')
cfg.from_envvar('TIGERGRADER_SETTINGS')


def report_error(msg, *args, **kwargs):
    raise Exception(msg.format(*args, **kwargs) + "\n")


def file_to_check(test):
    testdir = os.path.join(cfg["MODULE_FOLDER"], test)
    try:
        with file(os.path.join(testdir, "manifest.json")) as f:
            tests = json.load(f)
    except Exception as e:
        report_error("Could not find tests manifest {0}", e)

    return tests["plagiarism-check"]


def select_submissions(test):
    with closing(connect_db()) as db:
        c = db.execute("""SELECT upload,user,timestamp FROM (
                            SELECT test,user,timestamp,grade,upload
                            FROM grades
                            WHERE test == ?
                            ORDER BY grade ASC, timestamp DESC
                        ) as tmp group by test, user;""",
                       [test])
        return list(c)


def extract(upload, check_file):
    directory = mkdtemp()
    f = os.path.join(cfg["UPLOAD_FOLDER"], upload)
    z = ZipFile(f, 'r')
    z.extract(check_file, directory)
    z.close()
    return directory


def difference(test, s1, s2):
    check_file = file_to_check(test)
    d1 = extract(s1[0], check_file)
    d2 = extract(s2[0], check_file)
    try:
        check_output(['dwdiff', '-1', '-2', '-3', '-i', '-s',
                      os.path.join(d1, check_file),
                      os.path.join(d2, check_file)],
                     stderr=STDOUT)
        return 0
    except CalledProcessError as e:
        return int(e.output.split()[-2][:-1]) / 100.
    finally:
        shutil.rmtree(d1)
        shutil.rmtree(d2)


def read_check_file(test, upload):
    check_file = file_to_check(test)
    f = os.path.join(cfg["UPLOAD_FOLDER"], upload)
    z = ZipFile(f, 'r')
    data = z.read(check_file).decode('utf-8')
    z.close()
    return data


def check_plagiarism(test, threshold=0.30):
    submissions = select_submissions(test)
    report = []
    for i, s1 in enumerate(submissions):
        for j, s2 in enumerate(submissions):
            if i >= j:
                continue
            r = difference(test, s1, s2)
            if r < threshold:
                report.append([r,
                               {"upload": s1[0],
                                "user": s1[1],
                                "timestamp": s1[2]},
                               {"upload": s2[0],
                                "user": s2[1],
                                "timestamp": s2[2]}])
    report.sort()
    return report
