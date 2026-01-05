// PowerCV integration for brilliant-CV template
#import "@preview/brilliant-cv:3.1.1": cv, cv-section, cv-entry, cv-entry-start, cv-entry-continued
#import "@preview/fontawesome:0.5.0": *

// Convert PowerCV data to brilliant-CV metadata format
#let metadata = (
  language: "en",
  layout: (
    awesome_color: "skyblue",
    before_section_skip: "1pt",
    before_entry_skip: "1pt",
    before_entry_description_skip: "1pt",
    paper_size: "a4",
    fonts: (
      regular_fonts: ("Source Sans 3",),
      header_font: "Roboto",
    ),
    header: (
      header_align: "left",
      display_profile_photo: false,
      profile_photo_radius: "50%",
      info_font_size: "10pt",
    ),
    entry: (
      display_entry_society_first: true,
      display_logo: false,
    ),
    footer: (
      display_page_counter: false,
      display_footer: true,
    ),
  ),
  personal: (
    first_name: data.user_information.name.split(" ").at(0, default: "First"),
    last_name: data.user_information.name.split(" ").slice(1).join(" "),
    info: (
      email: data.user_information.email,
      phone: data.user_information.phone,
      linkedin: data.user_information.linkedin,
      github: data.user_information.github,
      location: data.user_information.address,
    ),
  ),
  lang: (
    en: (
      header_quote: data.user_information.profile_description,
      cv_footer: "Curriculum Vitae",
      letter_footer: "Cover Letter",
    ),
  ),
)

#show: cv.with(metadata)

// Professional Experience Section
#cv-section("Professional Experience")

#for experience in data.experiences {
  #if experience.job_title != "" {
    cv-entry-start(
      society: experience.company,
      location: experience.location,
    )

    cv-entry-continued(
      title: experience.job_title,
      date: experience.start_date + " - " + experience.end_date,
      description: experience.description.split("\n").filter(item => item != ""),
    )
  }
}

// Education Section
#cv-section("Education")

#for education in data.education {
  cv-entry(
    society: education.institution,
    title: education.degree + " in " + education.field_of_study,
    location: education.location,
    date: education.graduation_date,
    description: education.description,
  )
}

// Skills Section
#cv-section("Skills")

#let skills_list = ()
#for skill in data.skills {
  skills_list.push(skill.name + " (" + skill.proficiency + ")")
}

#cv-entry(
  title: "Technical Skills",
  description: skills_list,
)

// Projects Section (if available)
#if data.projects.len() > 0 {
  #cv-section("Projects")

  #for project in data.projects {
    cv-entry(
      title: project.name,
      society: project.organization,
      date: project.start_date + " - " + project.end_date,
      description: project.description,
    )
  }
}

// Certifications (if available)
#if data.certifications.len() > 0 {
  #cv-section("Certifications")

  #for cert in data.certifications {
    cv-entry(
      title: cert.name,
      society: cert.issuer,
      date: cert.issue_date + (cert.expiry_date != "" ? " - " + cert.expiry_date : ""),
      description: cert.description,
    )
  }
}
