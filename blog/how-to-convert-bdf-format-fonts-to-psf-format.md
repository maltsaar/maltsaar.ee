---
title = "How to convert BDF format fonts to PSF format"
description = "This is useful if you want to use a BDF format font as your Linux TTY console font"
published = "2023-08-01T00:00Z"
updated = "2025-01-15T21:00Z"
---

This is useful if you want to use a BDF format font as your Linux TTY console font.

This guide takes some liberties in assuming you are using Arch Linux but it should be fairly straightforward on other distros.

## Convert BDF to PSF format

Install bdf2psf
```shell
yay -S bdf2psf
```
Convert your BDF font to PSF format
```shell
sudo bdf2psf --fb scientifica-11.bdf \
    /usr/share/bdf2psf/standard.equivalents \
    /usr/share/bdf2psf/fontsets/Uni2.512+/usr/share/bdf2psf/useful.set \
    512 scientifica-psf.psf
```

## Change TTY font

```shell
setfont scientifica-psf.psf
```

## Change TTY font permanently

Move font to `/usr/share/kbd/consolefonts`
```shell
mv scientifica-11.psf /usr/share/kbd/consolefonts
gzip /usr/share/kbd/consolefonts/scientifica-11.psf
```

Set the font in `/etc/vconsole.conf`
```shell
FONT=scientifica
```

Rebuild initramfs
```shell
mkinitcpio -P
```

## What if I have a hiDPI screen?

You can make the font 2x bigger
```shell
setfont scientifica-psf.psf -o scientifica-psf-2x.psf
```
