import csv
from test_language_model_processor import SimpleLanguageModelProcessor

def main():
    # Sample Reddit comments about Nothing Phone 3a/3a Pro
    sample_comments = [
        "The Nothing Phone 3a is terrible. The battery life is awful and it keeps crashing.",
        "Really disappointed with my Nothing Phone 3a Pro. The camera quality is poor and the phone gets very hot.",
        "Having issues with the Nothing Phone 3a. The screen keeps freezing and the touch response is bad.",
        "The Nothing Phone 3a Pro is not working as expected. The battery drains too quickly.",
        "Terrible experience with Nothing Phone 3a. The software is buggy and the phone randomly restarts.",
        "The Nothing Phone 3a Pro has a faulty fingerprint sensor. It's the worst phone I've ever used.",
        "Disappointed with the Nothing Phone 3a. The build quality is poor and the buttons are loose.",
        "Having problems with my Nothing Phone 3a Pro. The screen has dead pixels and the touch doesn't work properly.",
        "The Nothing Phone 3a is awful. The speaker quality is terrible and the microphone doesn't work well.",
        "My Nothing Phone 3a Pro has a defect in the display. The colors are off and there's a visible line down the middle."
    ]

    # Initialize the processor
    processor = SimpleLanguageModelProcessor()

    # Process each comment
    for comment in sample_comments:
        processor.process_complaint(comment)

    # Get the processed complaints
    complaints = processor.get_complaints()

    # Write results to CSV
    with open('complaints_analysis.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Complaint', 'Count'])
        for complaint, count in complaints.items():
            writer.writerow([complaint, count])

    print("Analysis complete! Results have been saved to 'complaints_analysis.csv'")
    print("\nSummary of complaints:")
    for complaint, count in complaints.items():
        print(f"\nComplaint: {complaint}")
        print(f"Occurrences: {count}")

if __name__ == "__main__":
    main() 