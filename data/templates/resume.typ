// Self-contained Modern CV Template
#let cv(
  author: "",
  title: "",
  contact: (),
  body
) = {
  set document(author: author, title: title)
  set text(font: "Linux Libertine", lang: "en", size: 10pt)
  set page(margin: (x: 1.5cm, y: 1.5cm))
  set par(leading: 0.5em, justify: true) // Tighten line spacing

  // Header
  align(center)[
    #text(size: 18pt, weight: "bold")[#author] \
    #v(0.5em)
    #text(size: 9pt)[#contact.map(c => link(c.at(0))[#c.at(1)]).join(" | ")]
  ]
  
  // Body
  v(1em)
  body
}

#let position(title: "", company: "", place: "", date: "", body) = {
  pad(bottom: 4pt)[
    #grid(
      columns: (1fr, auto),
      row-gutter: 0.5em,
      align(left, strong(title)), align(right, date),
      align(left, emph(company)), align(right, emph(place))
    )
    #body
  ]
}

#let skills(..args) = {
  pad(top: 2pt, {
    for arg in args.pos() {
      box(inset: 2pt)[*#arg.at(0)*: #arg.at(1)]
      linebreak()
    }
  })
}

#show: cv.with(
  author: "<< data.user_information.name|typst_escape >>",
  title: "Professional",
  contact: (
    <% if data.user_information.email %>
    ("mailto:<< data.user_information.email|urlencode >>", "<< data.user_information.email|typst_escape_email >>"),
    <% endif %>
    <% if data.user_information.phone %>
    ("tel:<< data.user_information.phone|typst_escape >>", "<< data.user_information.phone|typst_escape >>"),
    <% endif %>
    <% if data.user_information.linkedin %>
    ("<< data.user_information.linkedin|typst_escape >>", "LinkedIn"),
    <% endif %>
    <% if data.user_information.github %>
    ("<< data.user_information.github|typst_escape >>", "GitHub"),
    <% endif %>
  ),
)

<% if data.user_information.profile_description %>
= Profile
<< data.user_information.profile_description|typst_escape >>
<% endif %>

<% if data.user_information.experiences %>
= Work Experience
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

<% if data.user_information.education %>
= Education
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

<% if data.user_information.skills or data.user_information.languages %>
= Skills
#skills(
  <% if data.user_information.languages %>
  ("Languages",
   "<% if data.user_information.languages is string %><< data.user_information.languages|typst_escape >><% else %><< data.user_information.languages|join(', ')|typst_escape >><% endif %>"),
  <% endif %>
  
  <% if data.user_information.skills is mapping %>
    <% if data.user_information.skills.hard_skills %>
    ("Tech", "<< data.user_information.skills.hard_skills|join(', ')|typst_escape >>"),
    <% endif %>
    <% if data.user_information.skills.soft_skills %>
    ("Soft Skills", "<< data.user_information.skills.soft_skills|join(', ')|typst_escape >>"),
    <% endif %>
  <% else %>
    ("Skills", "<< data.user_information.skills|join(', ')|typst_escape >>"),
  <% endif %>
)
<% endif %>
