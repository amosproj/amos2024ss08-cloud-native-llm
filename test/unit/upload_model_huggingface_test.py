import unittest
import os
import mock
from src.scripts import upload_model_huggingface

dirs = ['dir', 'sub_dir', 'sub_sub_dir', 'sub_sub_sub_dir']


def mocked_list_dirs(dir):
    if dir == dirs[0]:
        return [dirs[1]]
    elif dir == os.path.join(dirs[0], dirs[1]):
        return [dirs[2]]
    elif dir == os.path.join(dirs[0], dirs[1], dirs[2]):
        return [dirs[3]]
    elif dir == os.path.join(dirs[0], dirs[1], dirs[2], dirs[3]):
        return ['file_res.txt']
    return []


def mocked_is_file(file):
    if file == os.path.join(*dirs, 'file_res.txt'):
        return True
    return False


class UploadModelHuggingfaceTest(unittest.TestCase):

    @mock.patch('os.listdir', side_effect=mocked_list_dirs)
    @mock.patch('os.path.isfile', side_effect=mocked_is_file)
    def test_get_file_paths_recursive(self, mock_is_file, mock_listdir):
        self.assertEqual(upload_model_huggingface.get_file_paths(
            'dir'), ["/".join(dirs[1:]) + "/file_res.txt"])


UploadModelHuggingfaceTest().test_get_file_paths_recursive()
