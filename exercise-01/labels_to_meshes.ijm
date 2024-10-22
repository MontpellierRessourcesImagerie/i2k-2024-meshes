/**
 * This macro exports the currently opened labeled image (8 or 16 bits) into a sequence of OBJ files.
 * Each OBJ contains a label, and is named after this label.
 */

var OUTPUT_PATH = "/home/benedetti/Downloads/I2K/data/ascidian-labels/cells-obj-r2/";
var RESAMPLING  = 2;

function ask_options() {
	Dialog.create("Labels to meshes options");
	Dialog.addDirectory("Output folder", File.getDirectory("home"));
	Dialog.addNumber("Resampling factor", 2);
	Dialog.show();
	output_path = Dialog.getString();
	resampling = Dialog.getNumber();
	if (!File.isDirectory(output_path)) {
		print("The provided folder doesn't exist");
		exit;
	}
	if (resampling <= 0) {
		print("Resampling factor is > 0");
		exit;
	}
	OUTPUT_PATH = output_path;
	RESAMPLING  = resampling;
}

function join(root, leaf) {
	if (endsWith(root, File.separator)) {
		return root + leaf;
	}
	return root + File.separator + leaf;
}

function stack_max() {
	getDimensions(width, height, channels, slices, frames);
	maxi = 0; // max == nCells
	for (s = 1 ; s <= slices ; s++) {
		setSlice(s);
		getStatistics(area, mean, min, max, std, histogram);
		if (max > maxi) {
			maxi = max;
		}
	}
	return maxi;
}

function main() {
	ask_options();
	
	print("Starting...");
	run("Remap Labels");
	run("8-bit");
	run("Remap Labels");
	
	nItems = stack_max();
	
	for (i = 1 ; i <= nItems ; i++) {
		target = "slice_" + i;
		run("Duplicate...", "title=" + target + " duplicate");
		setThreshold(i, i, "raw");
		setOption("BlackBackground", true);
		run("Convert to Mask", "background=Dark black");
		output_path = join(OUTPUT_PATH, "item-" + IJ.pad(i, 3) + ".obj");
		run(
			"Wavefront .OBJ ...", 
			"stack=" + target + " threshold=1 resampling=" + RESAMPLING + " red green blue save=" + output_path
		);
		close();
		print("Exported item " + i + "/" + nItems);
	}
}

main();
print("DONE.");