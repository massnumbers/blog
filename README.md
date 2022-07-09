# Mass. Numbers blog

This is the latest incarnation of the Mass. Numbers blog that looks at
Massachusetts politics and policy through a quantitative lens. The
original version of the blog is at (http://massnumbers.blogspot.com).
The goal is to eventually import those articles into this framework.

The great thing about hosting the blog on GitHub and using the the
[Distill](https://rstudio.github.io/distill/blog.html) blogging
framework on top of [Rmarkdown](https://rmarkdown.rstudio.com/), is
that the site contains not only the readable HTML output, but also
contains all of the data and code used to make the maps,
visualizations, and models.

The Rmarkdown source files are in the `_posts` directory and get
compiled through a process called *knitting* into the
`docs/posts` directory. The supporting data files are in the
`_data` directory.

In addition to the Distill and Rmarkdown frameworks, the other
essential tool that makes the interactive maps on this site is the
(tmap)[https://cran.r-project.org/web/packages/tmap/vignettes/tmap-getstarted.html]
package the switches seamlessly between creating static map plots, and
interactive web-based maps using [leaflet](https://leafletjs.com/). I
have been looking for an easy-to-use interactive mapping framework
ever since the demise of Google Fusion Tables.

I am hoping that this exercise in transparency, including the data,
code, and analysis in one open repository, will give a demonstration
of open journalism and reproducible social science.



