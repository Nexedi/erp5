editor_list = [("Default", "default")]

if context.getPreferredSourceCodeEditor() == 'codemirror':
  editor_list.extend([("Emacs", "emacs"), ("Vim", "vim")])

return editor_list
