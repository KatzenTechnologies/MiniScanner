rule NightshadeC2_Win_x64
{
    meta:
        author = "YungBinary"
        description = "Detects NightshadeC2 in memory"

    strings:
        $a = "camera!" wide
        $b = "keylog.txt" wide
        $c = "powershell Start-Sleep -Seconds 3; Remove-Item -Path %ws -Force" wide
        $d = "MachineGuid" wide
        $e = "[%02d:%02d %02d.%02d.%02d] %ws"

    condition:
        4 of them
}

rule NightshadeC2_Python_Win
{
    meta:
        author = "YungBinary"
        description = "Detects PyNightshade on disk"

    strings:
        $s1 = "Winhttp.WinHttpOpenRequest(hConnect, \"GET\", \"line/?fields=" ascii
        $s2 = "MachineGuid" ascii
        $s3 = "i = (i + 1) % 256" ascii

    condition:
        all of them
}