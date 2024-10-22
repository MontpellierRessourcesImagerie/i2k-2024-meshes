getDimensions(width, height, channels, slices, frames);
n_points = 500;

for (i = 0 ; i < n_points ; i++) {
	x = floor(random * width);
	y = floor(random * height);
	z = floor(random * slices)+1;
	setSlice(z);
	setPixel(x, y, 65000);
}
