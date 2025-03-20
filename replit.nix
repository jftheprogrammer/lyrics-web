{pkgs}: {
  deps = [
    pkgs.glibcLocales
    pkgs.ffmpeg-full
    pkgs.postgresql
    pkgs.openssl
  ];
}
