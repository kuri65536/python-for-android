# this sample came from:
#   http://stackoverflow.com/questions/37795626/file-dialog-in-python-sl4a
# and fixed PEP8 errors.
import android
import os

droid = android.Android()
# Specify root directory and make sure it exists.
base_dir = '/sdcard/sl4a/scripts/'
if not os.path.exists(base_dir):
    os.makedirs(base_dir)


def show_dir(path=base_dir):
    """Shows the contents of a directory in a list view."""
    # The files and directories under "path"
    nodes = os.listdir(path)
    # Make a way to go up a level.
    if path != base_dir:
        nodes.insert(0, '..')
    droid.dialogCreateAlert(os.path.basename(path).title())
    droid.dialogSetItems(nodes)
    droid.dialogShow()
    # Get the selected file or directory .
    result = droid.dialogGetResponse().result
    droid.dialogDismiss()
    if 'item' not in result:
        return
    target = nodes[result['item']]
    target_path = os.path.join(path, target)
    if target == '..':
        target_path = os.path.dirname(path)
    # If a directory, show its contents .
    if os.path.isdir(target_path):
        show_dir(target_path)
    # If an file display it.
    else:
        droid.dialogCreateAlert('Selected File', '{}'.format(target_path))
        droid.dialogSetPositiveButtonText('Ok')
        droid.dialogShow()
        droid.dialogGetResponse()


if __name__ == '__main__':
    show_dir()

# vi: ft=python:et:ts=4:nowrap
