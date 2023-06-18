---
title: "Contributing Knowledge Articles"
permalink: pages/contribute
---

### Contributing a Knowledge Article

* If you have a .md file ready please put it in the /pages folder and create a pull request
* If you have an existing document that needs to be converted to .md we suggest using Pandoc or another tool


### Convert Tools

* Pandoc
  https://pandoc.org/installing.html


After you install pandoc you can convert your document into an .md file: (no spaces in filename)

    pandoc -s [name-of-your-file].docx -t markdown -o [name-of-the-md-file].md


### Pandoc Support & Known Issues

* The filename cannot contain spaces. e.g. <read me.docx> must be <read_me.docx>

