# Design Philosophy Images

This directory contains reference images that define the visual style for comic generation.

## Supported Styles

### amar_chitra_katha
- File: `amar_chitra_katha.jpg`
- Description: Traditional Indian comic book style with detailed illustrations, vibrant colors, and classical art influences

### xkcd  
- File: `xkcd.jpg`
- Description: Simple stick figure style with minimal details, black lines on white background

## Usage

When generating comics, these reference images are sent to the AI along with the panel description to ensure consistent visual style matching the chosen philosophy.

## Adding New Styles

1. Add a new reference image file: `{style_name}.jpg`
2. Update the ConfigService to include the new style
3. The system will automatically use the reference image when that style is selected