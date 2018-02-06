# ZotLife

- Powerful tool (currently just the backend) designed to schedule university courses. 
- Currently supports SOCIOLOGY at UCI, but the framework is designed to be able to support
  any major at any university with various requirements and timeframes.
- Currently reads in course info/major requirements from a .maj file in the framework
  and builds course schedules/valid 4-year plans (tuned/created using parameters, e.g. 
  number of units per quarter, likelihood of course being offered, preference of one 
  course over another, substitute courses, units allowed per quarter, blocked out units
  per quarter for electives, etc. See runtime_vars in main/main.py and text in 
  universities/SSU/majors/major.BS.16-17 to further see power/flexibility of framework.)
- Capable of creating hundreds or thousands of possible valid major academic plans 
 (all of which are near-optimal based off of likelihood course is offered, and user preference)
 in seconds
- stats/ and utility_scripts/ are for gathering information to enhance the framework under main/
- For now the framework only schedules courses, not individual classes. In other words, a 4 year
 plan can be generated, but not a weekly schedule of class times for the quarter/semester.

See main/README for framework implementation details. 
