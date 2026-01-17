# E-Bodha: Academic information management system
This is an academic management system used for executive program students. The program would be used to track student progress, submission of grades, generation of grade cards, transcripts and certificates. The program would also allow the teachers and administrators to view and modify information.

## Users & Stakeholders
There are two types of users in the system, student users and non-student users.
  * Student users are identified with an unique alphanumeric ID number assigned to them. The ID number starts with "EMT" followed by two digit year followed by two character course code and then four digit serial number.  
  * Non student users are identified by a unique alphanumeric name used as login ID. 

Every user has a name, gender, address, phone number and email.

## Roles
The Roles in the system are student, alumni, teacher, administrator.
### Student
A student is admitted for a particular discipline. A student also goes through physical verification. A student also registers for a semester to attend courses of his/her discipline. A student can view his/her grade for every registered course once it is available.
### Alumni
A student after passing out is assigned the role of alumni. An alumni can not register for any course. An alumni can view the grades of their already registered courses.
### Teachers
A teacher teaches zero or more courses in a semester. A teacher uploads marks of each of the tests for each of the students atending course and appear for the test. The teacher also assigns grades to students attending his/her course at the end of course.
### Administrator
An administrator can do all the changes allowed in the system.

Student users can only be assigned student or alumni role. Non-student users can be assigned any role. Administrator is only allowed to create user, role and assign or change roles of users.

## Other enitities in the system

### Semester
A semester has a start date and an end date. A semester has an associated academic calendar.
### Academic Calendar
An academic calendar consists of a start and end date for a set of events. The set of events is dynamic and can chnage. The universe of events monotonically increases.
### Course
A course consists of the following properties
  * course code: Alphanumeric and unique.
  * course name: Alphanumeric
  * course Category: Category can be one of the following: Core Couse, Elective, MTech Thesis, MTech Project. The list allowed course categories may change.
  * Lecture Credits: Number
  * Tutorial Credits: Number
  * Practice Credits: Number
A course can be in different state. Initially it is created in the "Available" state. A set of courses can be offered for registration in a specific semester. The course offered for registration in semester 1 must be uniquely identified from the same course offered for registration in semester 2. A course offered for registration in a semester is only available with the duration of the semester as per academic calendar. As per academic calendar students can register only to the courses offered for registration in the running semester. An available course can be offered for registration in multiple semesters.

A course can be taught by one or more teachers. A course consists of multiple examination each having a unique name. A course may not have some of the examinations. For each examination and each student registered for course, there would be a marks given. Finally, for a course each student registered for the course gets a grade. A grade has a corresponding numeric point associated with it. The set of examinations and set of grades and their corresponding numeric points are fixed and can only be changed by Administrator. Any change in the set of examination and grade are time-stamped. Grades obtained with a defined set of grades should always be considered with the same point mapping even though later it may be changed.

A special examination called "Supplementary examination" my be conducted for each course. Students who have registered for a course can also register for the supplemntary examination of that course. Only those who have registered for the supplementary examination of a course would recieve a separate grade for supplementary examination of that course. If a student appears for supplementary examination, the grade obtained in supplementary examination is considered as the grade for the course than the grade allotted before supplementary examination.

### SGPA and CGPA
For a semester the Semester Grade Point Average (SGPA) is computed by taking a weighted sum of the grade points obtained for the courses in that semester.
A Cumulative Grade Point Average (CGPA) of a student at any point of time is the weighted sum of the grade points obtained for all the courses till that point.