import os
from django.core.files.storage import FileSystemStorage as DjangoFileSystemStorage
from django.core.files import File


class FileSystemStorage(DjangoFileSystemStorage):
    OS_OPEN_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0) | os.O_TRUNC

    def save(self, name, content, max_length=None):
        """
        去掉可用路径检测，直接写入目的路径
        """
        if name is None:
            name = content.name

        if not hasattr(content, 'chunks'):
            content = File(content, name)

        # name = self.get_available_name(name, max_length=max_length)
        return self._save(name, content)

    def mkdir(self, name):
        """ 创建指定路径文件夹 """
        full_path = self.path(name)

        # Create any intermediate directories that do not exist.
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            try:
                if self.directory_permissions_mode is not None:
                    # os.makedirs applies the global umask, so we reset it,
                    # for consistency with file_permissions_mode behavior.
                    old_umask = os.umask(0)
                    try:
                        os.makedirs(directory, self.directory_permissions_mode)
                    finally:
                        os.umask(old_umask)
                else:
                    os.makedirs(directory)
            except FileExistsError:
                # There's a race between os.path.exists() and os.makedirs().
                # If os.makedirs() fails with FileExistsError, the directory
                # was created concurrently.
                pass
        if not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)

    def _save(self, name, content):
        self.mkdir(name)
        with open(name, 'wb') as f:
            f.write(content.read())

        return name


file_system_storage = FileSystemStorage()
