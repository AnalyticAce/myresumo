// PowerCV integration for simple-xd-resume template
#import "@preview/simple-xd-resume:0.1.0": make-resume

#show: make-resume.with(
  font: "Source Sans 3",
  margin: 1in,
  firstname: data.user_information.name.split(" ").at(0, default: "First"),
  lastname: data.user_information.name.split(" ").slice(1).join(" "),
  headlines: (
    (name: data.user_information.main_job_title or "Professional", linkto: ""),
  ),
  email: data.user_information.email,
  phone-number: data.user_information.phone,
  github: if data.user_information.github != none {
    (username: data.user_information.github)
  } else {
    none
  },
  linkedin: if data.user_information.linkedin != none {
    (username: data.user_information.linkedin)
  } else {
    none
  },
  telegram: none,
  homepage: none,
  experiences: data.experiences.map(exp => (
    organization: exp.company,
    startdate: exp.start_date,
    enddate: if exp.end_date != "" { exp.end_date } else { "Present" },
    title: exp.job_title,
    responsibilities: exp.description.split("\n").filter(item => item != ""),
    label: "",
  )),
  educations: data.education.map(edu => (
    institution: edu.institution,
    startdate: "",
    enddate: edu.graduation_date,
    degree: edu.degree + " in " + edu.field_of_study,
    gpa: none,
    location: edu.location,
    highlights: edu.description.split("\n").filter(item => item != ""),
  )),
  projects: data.projects.map(proj => (
    name: proj.name,
    startdate: proj.start_date,
    enddate: if proj.end_date != "" { proj.end_date } else { "Present" },
    organization: proj.organization or "Personal Project",
    technologies: (),
    highlights: proj.description.split("\n").filter(item => item != ""),
  )),
  skills: (
    languages: (),
    frameworks: (),
    tools: (),
    methodologies: (),
    soft-skills: (),
  ),
  certifications: data.certifications.map(cert => (
    name: cert.name,
    issuer: cert.issuer,
    date: cert.issue_date,
    url: none,
  )),
)