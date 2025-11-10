#!/usr/bin/env python3
"""
Visual demonstration of estimated images calculation.
Shows how the calculation works with different parameters.
"""

def calculate_estimated_images(words, wpm, interval):
    """Calculate estimated images for given parameters."""
    duration_minutes = words / wpm
    duration_seconds = duration_minutes * 60
    estimated_images = int(duration_seconds / interval)
    return {
        'words': words,
        'wpm': wpm,
        'interval': interval,
        'duration_minutes': duration_minutes,
        'duration_seconds': duration_seconds,
        'estimated_images': estimated_images
    }


def print_calculation(result):
    """Print calculation in a nice format."""
    print(f"  Words: {result['words']:,}")
    print(f"  Narration Speed: {result['wpm']} words/minute")
    print(f"  Frame Interval: {result['interval']} seconds")
    print(f"  → Duration: {result['duration_minutes']:.2f} minutes ({result['duration_seconds']:.0f} seconds)")
    print(f"  → Estimated Images: {result['estimated_images']:,}")
    print()


def main():
    print("=" * 70)
    print("ESTIMATED IMAGES CALCULATION DEMONSTRATION")
    print("=" * 70)
    print()
    print("Formula: Images = (Words / WPM * 60) / Interval")
    print()
    
    # Test cases matching common scenarios
    scenarios = [
        ("Standard biography (12,000 words)", 12000, 150, 6.0),
        ("Short biography (5,000 words)", 5000, 150, 6.0),
        ("Long biography (15,000 words)", 15000, 150, 6.0),
        ("Faster narration (12,000 words @ 180 wpm)", 12000, 180, 6.0),
        ("Slower narration (12,000 words @ 120 wpm)", 12000, 120, 6.0),
        ("Shorter intervals (12,000 words @ 3s)", 12000, 150, 3.0),
        ("Longer intervals (12,000 words @ 10s)", 12000, 150, 10.0),
    ]
    
    for i, (description, words, wpm, interval) in enumerate(scenarios, 1):
        print(f"Scenario {i}: {description}")
        result = calculate_estimated_images(words, wpm, interval)
        print_calculation(result)
    
    print("=" * 70)
    print("HOW IT WORKS IN THE GUI:")
    print("=" * 70)
    print()
    print("1. The GUI has sliders for:")
    print("   - Frame Interval (3-30 seconds, default: 6s)")
    print("   - Narration Speed (100-200 wpm, default: 150 wpm)")
    print()
    print("2. When you adjust these sliders, the GUI:")
    print("   - Uses a default of 12,000 words as an estimate")
    print("   - Calculates: duration = 12000 / narration_speed * 60")
    print("   - Calculates: images = duration / frame_interval")
    print("   - Updates the 'Estimated images' label")
    print()
    print("3. When actually processing a file:")
    print("   - The real word count from the file is used")
    print("   - More accurate calculation is performed")
    print("   - Timeline is calculated in text_processor.py")
    print()
    print("=" * 70)
    print("CODE LOCATION:")
    print("=" * 70)
    print()
    print("GUI calculation:")
    print("  File: gui/main_window.py")
    print("  Function: _update_estimated_images() (line 356)")
    print()
    print("Actual processing calculation:")
    print("  File: processing/text_processor.py")
    print("  Function: calculate_timeline() (line 80)")
    print()


if __name__ == "__main__":
    main()
