import os
import sublime_plugin


class EePrependModCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not self.is_valid_file():
            return

        if self.is_prepended_module_file_opened():
            original_filepath = self.view.file_name().replace('ee', '')
            return self.view.window().open_file(original_filepath)

        prepended_module_path = self.build_prepended_module_path()
        klass_name = self.build_klass_name(prepended_module_path)

        if not self.is_prepend_mod_line_exist():
            self.add_prepend_mod_line(edit, klass_name)

        if not os.path.exists(prepended_module_path):
            create_file(
                prepended_module_path,
                self.build_prepended_module_skeleton(klass_name)
            )

        self.view.window().open_file(prepended_module_path)

    def build_prepended_module_path(self):
        original_path = self.view.file_name()
        paths = original_path.split('/')

        if 'app' in paths:
            main_folder_name = 'app'
        elif 'lib' in paths:
            main_folder_name = 'lib'

        main_folder_index = paths.index(main_folder_name)
        root_path = '/'.join(
            paths[:main_folder_index] + [f'ee/{main_folder_name}/']
        )

        if main_folder_name == 'app':
            if 'concerns' in paths:
                return root_path + '/'.join(
                    paths[main_folder_index + 1:-1] + ['ee', paths[-1]]
                )
            else:
                return root_path + '/'.join(
                    [paths[main_folder_index + 1], 'ee'] +
                    paths[main_folder_index + 2:]
                )

        return root_path + '/'.join(
            ['ee'] + paths[main_folder_index + 1:]
        )

    def build_klass_name(self, prepended_module_path):
        # Finds <klass_path> start index from string (ee/.../ee/<klass_path>)
        start_index = prepended_module_path.rindex('ee') + 2
        # Filepath has extension `.rb`
        end_index = prepended_module_path.index('.')

        klass_path = prepended_module_path[start_index:end_index]
        # Camelize & glue together with `::`
        return klass_path.title().replace('_', '').replace('/', '::')[2:]

    # Actions

    def add_prepend_mod_line(self, edit, klass_name):
        self.view.insert(edit, self.view.size(), f"\n{klass_name}.prepend_mod")
        self.view.run_command('save')

    # Helper methods

    def is_valid_file(self):
        file_name = self.view.file_name()
        if not '.rb' in file_name:
            return False

        if 'ee' in file_name and not self.is_prepended_module_file_opened():
            return False

        if 'app/' not in file_name and 'lib/' not in file_name:
            return False

        return True

    def is_prepended_module_file_opened(self):
        return self.view.file_name().count('ee') == 2

    def is_prepend_mod_line_exist(self):
        last_line_number = self.view.rowcol(self.view.size())[0]

        prelast_line_point = self.view.text_point(last_line_number - 1, 0)
        prelast_line_region = self.view.line(prelast_line_point)
        prelast_line_content = self.view.substr(prelast_line_region)

        return 'prepend_mod' in prelast_line_content

    def build_prepended_module_skeleton(self, klass_name):
        skeleton = '# frozen_string_literal: true\n\n'
        namespaces = ['EE'] + klass_name.split('::')
        indent = 0

        for namespace in namespaces:
            skeleton += f"{indent * ' '}module {namespace}\n"
            indent += 2

        skeleton += f"{indent * ' '}extend ::Gitlab::Utils::Override\n"

        while indent != 0:
            indent -= 2
            skeleton += f"{indent * ' '}end\n"

        return skeleton


def create_file(filename, data):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'w') as file:
        file.write(data)
