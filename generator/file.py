import os


def write(_filepath, _contents, _overwrite):
    if os.path.exists(_filepath) and not _overwrite:
        return
    print("write " + _filepath)
    with open(_filepath, "w", encoding="utf-8") as wf:
        wf.write(_contents)
        wf.close()
