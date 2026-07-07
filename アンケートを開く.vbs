Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
folder = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = folder

' サーバーを別ウィンドウで起動
shell.Run "cmd /c """ & folder & "\start.bat""", 1, False

' 起動待ち
WScript.Sleep 4000

' ブラウザでアンケートを開く
shell.Run "http://localhost:5000", 1, False
