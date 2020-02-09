@echo off
for /r %1 %%f in (*.png) do (
	echo Processing "%%~nf%%~xf"...
	ImageResizer-r129.exe /load "%%~ff" /resize auto "EPXB" /save "%%~df%%~pf%%~nf_%%~xf" >nul 2>&1
	del "%%~ff"
	ren "%%~df%%~pf%%~nf_%%~xf" "%%~nf%%~xf"
)
pause