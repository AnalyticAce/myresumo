// Modern Side-Column CV Template
#let modern_cv(
  author: "",
  title: "",
  contact: (),
  skills_content: [],
  body
) = {
  set document(author: author, title: title)
  set text(font: "Roboto", lang: "en", size: 10pt)
  set page(margin: (x: 0cm, y: 0cm)) // Full bleed for sidebar

  // Define colors
  let primary_color = rgb("#2c3e50")
  let sidebar_color = rgb("#f5f7fa")
  let accent_color = rgb("#3498db")

  grid(
    columns: (30%, 70%),
    rows: (100%),
    // Sidebar
    rect(
      width: 100%, 
      height: 100%, 
      fill: sidebar_color,
      inset: (x: 1.5em, y: 3em),
    )[
      #align(center)[
        #text(size: 20pt, weight: "bold", fill: primary_color)[#author] \
        #v(0.5em)
        #text(size: 11pt, style: "italic", fill: accent_color)[#title]
      ]
      
      #v(2em)
      
      // Contact Info
      #align(left)[
        #for c in contact {
           box(inset: (bottom: 0.5em))[
             *#c.at(1)* \
             #link(c.at(0))[#text(size: 9pt)[#c.at(0)]]
           ]
        }
      ]
      
      #v(2em)
      *Skills* \
      #skills_content
    ],
    
    // Main Content
    rect(
      width: 100%,
      height: 100%,
      fill: white,
      inset: (x: 2em, y: 3em)
    )[
      #body
    ]
  )
}

#let position(title: "", company: "", place: "", date: "", body) = {
  pad(bottom: 1em)[
    #grid(
      columns: (1fr, auto),
      align(left, strong(title)), align(right, text(style: "italic")[#date]),
      align(left, emph(company)), align(right, emph(place))
    )
    #v(0.3em)
    #body
  ]
}

#show: modern_cv.with(
  author: "<< data.user_information.name|typst_escape >>",
  title: "Professional",
  contact: (
    <% if data.user_information.email %>
    ("<< data.user_information.email|typst_escape_email >>", "Email"),
    <% endif %>
    <% if data.user_information.phone %>
    ("<< data.user_information.phone|typst_escape >>", "Phone"),
    <% endif %>
    <% if data.user_information.linkedin %>
    ("<< data.user_information.linkedin|typst_escape >>", "LinkedIn"),
    <% endif %>
    <% if data.user_information.github %>
    ("<< data.user_information.github|typst_escape >>", "GitHub"),
    <% endif %>
  ),
  skills_content: [
    <% if data.user_information.skills or data.user_information.languages %>
      <% if data.user_information.languages %>
       *Languages* \
       <% if data.user_information.languages is string %><< data.user_information.languages|typst_escape >><% else %><< data.user_information.languages|join('\\\\ ')|typst_escape >><% endif %>
       #v(1em)
      <% endif %>
      
      <% if data.user_information.skills is mapping %>
        <% if data.user_information.skills.hard_skills %>
        *Tech* \
        << data.user_information.skills.hard_skills|join(', ')|typst_escape >>
        #v(1em)
        <% endif %>
        <% if data.user_information.skills.soft_skills %>
        *Soft Skills* \
        << data.user_information.skills.soft_skills|join(', ')|typst_escape >>
        <% endif %>
      <% else %>
        *Skills* \
        << data.user_information.skills|join(', ')|typst_escape >>
      <% endif %>
    <% endif %>
  ]
)

<% if data.user_information.profile_description %>
= Profile
<< data.user_information.profile_description|typst_escape >>
#v(1em)
<% endif %>

<% if data.user_information.experiences %>
= Work Experience
#v(0.5em)
<% for exp in data.user_information.experiences %>
#position(
  title: "<< exp.job_title|typst_escape >>",
  company: "<< exp.company|typst_escape >>",
  place: "<< exp.location|typst_escape >>",
  date: [<< exp.start_date|format_date >> -- << exp.end_date|format_date >>],
)[
  <% for task in exp.four_tasks %>
  - << task|typst_escape >>
  <% endfor %>
]
<% endfor %>
<% endif %>

<% if data.projects %>
= Projects
#v(0.5em)
<% for project in data.projects %>
#position(
  title: "<< project.project_name|typst_escape >>",
  company: [<% if project.tech_stack %><< project.tech_stack|join(', ')|typst_escape >><% endif %>],
  date: [],
)[
  <% for goal in project.two_goals_of_the_project %>
  - << goal|typst_escape >>
  <% endfor %>
  <% if project.project_end_result %>
  - *Result*: << project.project_end_result|typst_escape >>
  <% endif %>
]
<% endfor %>
<% endif %>

// Education (Added to Main Column)
<% if data.user_information.education %>
= Education
#v(0.5em)
<% for edu in data.user_information.education %>
#position(
  title: "<< edu.degree|typst_escape >>",
  company: "<< edu.institution|typst_escape >>",
  place: "<< edu.location|typst_escape >>",
  date: [<< edu.start_date|format_date >> -- << edu.end_date|format_date >>],
)[
  <% if edu.description %>
  << edu.description|typst_escape >>
  <% endif %>
]
<% endfor %>
<% endif %>
