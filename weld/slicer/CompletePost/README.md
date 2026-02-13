# Post Processor to run GCODE output from a 3D printer slicer on the WAAM Cell

## How to Use
1. Slice a part using the associated slicing profile in ORCA slicer. The layer height will automatically be detected by the code, but note this number down for later adjustment if necessary. This can be changed as needed, 0.5mm is a default value to give reasonably precise height adjustment while maintaining reasonable file size.
2. Place the Gcode file into the input folder, make sure this folder only contains one Gcode file
3. In WAAMGcodePost, set only slicing_flag to True
4. Adjust offsets under #SLICING PARAMETERS as needed
5. Run WAAMGcodePost in the terminal, this will create a folder structure containing the relative position along with the joint space configuration
6. IF the ../CompletePost/parts/"Your File Name Here"/ folder has more than one file named "sliced output", set file_number_index to the extension number on your file
7. Configure your weld job with the parameters under #WELDING PARAMETERS
8. Conduct a motion test by setting only motion_test_flag to True and running WAAMGcodePost.py from the terminal
9. If entirely manual layer height setting is desired, set flir_on to False 
10. If the motion test looks good, set only print_flag to True and run WAAMGcodePost.py from the terminal again
11. Follow prompts on screen, then wait for the driver commands to run and create two pop-up terminals, one for the flir and one for the fronius
12. Once the drivers have initialized, begin welding and follow on screen prompts
12.a While running, the layer height output should be the total height from the buildplate to the part, if not correct, input the correct number to the nearest layer height increment

## WAAMGcodePost

## parse_gcode
This function extracts coordinates from a GCode file and returns a set of csv files compatible with standard RPI WAAM functionality

## baseline_joint_func
This function converts coordinate positions found in a set of csv files into joint space configurations for both the welder and the positioner
This is a function definition around the default baseline_joint.py script found in Motoman

## weld_sliced_func
This function executes the weld job give input parameters, records data, and provides an interface for layer adjustments and segment pauses
