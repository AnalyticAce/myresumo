// Basic Typst Cover Letter Template
#let cover_letter(
  author: "",
  contact: (),
  recipient: "",
  body
) = {
  set document(author: author, title: "Cover Letter")
  set text(font: "Linux Libertine", lang: "en", size: 11pt)
  set page(margin: (x: 2.5cm, y: 2.5cm))
  set par(leading: 0.8em, justify: true)

  // Header
  align(center)[
    #text(size: 16pt, weight: "bold")[#author] \
    #v(0.5em)
    #text(size: 10pt)[#contact.map(c => c).join(" | ")]
  ]
  
  v(2em)
  
  // Date
  align(right)[#datetime.today().display("[day] [month repr:long] [year]")]
  
  v(1em)
  
  // Content
  body
}

#show: cover_letter.with(
  author: "<< data.user_information.name|typst_escape >>",
  contact: (
    <% if data.user_information.email %>"<< data.user_information.email|typst_escape_email >>",<% endif %>
    <% if data.user_information.phone %>"<< data.user_information.phone|typst_escape >>",<% endif %>
    <% if data.user_information.address %>"<< data.user_information.address|typst_escape >>",<% endif %>
  ),
)

// Body Content (Assumes 'cover_letter_content' is passed in data)
<< data.cover_letter_content|typst_escape >>
