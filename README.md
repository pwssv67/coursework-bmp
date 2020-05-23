# coursework-bmp
A little coursework about reading, writing and base-editing (resize and convert from palette to non-palette) bmp.
Files are not identical, but all pixels are exact same, all diference is in info header.

Resize is really basical, it just skips rows/lines or copies them.
Reading is based on struct.unpack, just as writing - on struct.pack.

Still have no idea how and why count resolution per meter.
Btw, should say, that pixels in bmp are written left-to-right and down-to-up.
Probably, it's a well-known fact, but it took me about half hour to figure out what's wrong.

Somewhen there will be interface, just for lulz.
