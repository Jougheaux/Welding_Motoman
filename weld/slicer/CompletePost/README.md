# Post Processor to run GCODE output from a 3D printer slicer on the WAAM Cell

## How to Use
1. Slice a part using the associated slicing profile in ORCA slicer. The layer height will automatically be detected by the code, but note this number down for later adjustment if necessary. This can be changed as needed, 0.5mm is a default value to give reasonably precise height adjustment while maintaining reasonable file size.
2. Place the Gcode file into the input folder, make sure this folder only contains one Gcode file
3. In WAAMGcodePost, set slicing_flag to True and print_flag to False
4. Adjust offsets under #SLICING PARAMETERS as needed
5. Run WAAMGcodePost in the terminal, this will create a folder structure containing the relative position along with the joint space configuration
6. In WAAMGcodePost, set slicing_flag to False and print_flag to True
7. IF the ../CompletePost/parts/"Your File Name Here"/ folder has more than one file named "sliced output", set file_number_index to the extension number on your file
8. Configure your weld job with the parameters under #WELDING PARAMETERS
9. Conduct a motion test by setting ARCON and flir_on to False and running WAAMGcodePost.py from the terminal
10. If the motion test looks good, set ARCON and flir_on to True and run WAAMGcodePost.py from the terminal again
11. Follow prompts on screen, then wait for the driver commands to run and create two pop-up terminals, one for the flir and one for the fronius
12. Once the drivers have initialized, begin welding and follow on screen prompts
12.a While running, the layer height output should be the total height from the buildplate to the part, if not correct, input the correct number to the nearest layer height increment

## WAAMGcodePost

## parse_gcode

## baseline_joint_func

## weld_sliced_func
