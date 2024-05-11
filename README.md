# Render Scheduler

This addon is a simple interface to set up a schedule for rendering stills with different cameras, world settings and visible collections without having to set those up manually each time. 

## Installation

Download the zip and extract contents or clone this repo, then inside Blender follow `Edit` > `Preferences` > `Add-ons` > `Install` and navigate to your downloaded `.py` file, select it and click `Install Add-on`. 
Once it has been installed enable it and the `Render` tab should appear on the right of your `3D Viewport`, if not press the `n` key. 

## Usage

The Render Scheduler tab is located in `3D Viewport` > `Sidebar` > `Render`  

![Render Tab](/img/screenshot_1.png)

Here you can add new render configurations to the schedule or remove them.

The options you can set are:

- `Name`: The name of this render config that will also be used as the output file name

- `Active`: The camera icon that tells the renderer to render the current configuration 

- `Filepath`: the path to the directory where the renders will be saved

- `Camera`: The active camera  

- `World`: The active `World` node tree

- `Collections`: The visible and hidden collections 

- `Samples`: The sample count to use 

- `Format`: Output format (this also sets the output file extension)

- `Color Depth/Float Depth`: Bit depth per channel

- `Compression/Quality`: Compression used for PNG format, Quality for JPEG format

- `Codec`: Compression codec for OpenEXR format


## Contributing


Contributions, bug fixes and suggestions are always welcome! Here are some guidelines to help you get started:

1. **Fork and Clone the Repository**: Start by forking the repository and then clone it to your local machine. This allows you to work on the project without affecting the main codebase.

2. **Create a New Branch**: For each new feature or bug fix, create a new branch. This keeps your work isolated and makes it easier to integrate your changes later.

3. **Write Clear Commit Messages**: A good commit message should describe what changes have been made and why. This helps others understand the history of the project.

4. **Test Before Submitting**: Please test your changes thoroughly before submitting a pull request. This helps maintain the quality of the code and reduces the chances of introducing bugs.

5. **Submit a Pull Request**: Once your changes are ready and tested, submit a pull request. Provide a detailed explanation of your changes and why they were made.

6. **Keep Your Branch Up to Date**: Regularly pull changes from the main repository to your fork to keep it up to date. This helps avoid merge conflicts.

