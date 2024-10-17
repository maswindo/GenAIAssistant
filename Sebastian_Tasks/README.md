# Currently In-Progress

## Use Case 1: Job Listing Compatability
CV/Resume Similarity to job description using key value padding for it (JSON format as a list of skills).
Checks the URL from a Linkedin Job given and it tries to store and parse the data from job description.

It needs to take the user profile, job description and between the two use semantic similarity to score the resume and description and give it a rating from the sub-string matching.

The two values most important to calculate for the similarities is skill and experience.

There should be the ability to have 1 job or a ranking of several jobs, sorted through compatability score.

# Future Implementation

## Use Case 2: User Profile Personalization
Create filter settings that are saved as User Data. These filters will be for parts that cannot be analyzed from a resume alone, such as: Benefits, Location, Hours, Overtime, Salary Range.

The filters show have a ranking of importance (Non-negoitable, and negoitable). Allow the filters to have a modifer that alters the ranking or compatability of a job versus it's applicant.
