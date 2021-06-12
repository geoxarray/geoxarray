FAQ
===

What's the status of this project?
----------------------------------

As of mid-2021 Geoxarray is being actively developed, but slowly. Geoxarray
is still in its early stages and will heavily depend on other projects like
xarray, rasterio, pyresample, and pyproj. Some of the intended features for
Geoxarray are still wishful thinking and will depend on changes
in other scientific Python libraries and decisions by the larger community
that Geoxarray will get the most of Geoxarray.

Want to help move development along? See the :doc:`contributing` page for
information on how to contribute including submitting feedback and viewing
existing bug reports and feature requests.

.. _doc_organization:

How is this documentation structured?
-------------------------------------

The Geoxarray project is trying hard to stick to the documentation structure
described in `this presentation <https://youtu.be/t4vKPhjcMZg>`_
by Daniele Procida. This is partly as an experiment to see how a new project
can fit into this "rigid" structure. It is also an experiment as there aren't
many projects in the geospatial scientific python ecosystem that makes these
hard boundaries between sections of their documentation. Is it working?

* Tutorials (Learning Oriented):
  Teach the user what they might want to do and walk them through it.
  Longer form instructions on how to go from nothing to something useful.
  Tutorials avoid a lot of detail to stay focused on finished a task. This
  means they also won't list all the available options/choices either.
  A tutorial will decide what the user does and accomplishes.
* How-To (Problem Oriented):
  Recipes to solve a specific problem. Less hand-holding and more
  straight to the point. In general these will be shorter than tutorials as
  they assume the user already knows a little bit about what they're doing.
  Explanation of how Geoxarray works is limited in how-tos and will generally
  go in "Topics". Similar to Tutorials, we limit explanation so that we can
  act and accomplish things as quickly as possible. A user finds a how-to
  because they know they have a specific problem they want to solve.
* Reference (Information Oriented):
  Low-level details about the interfaces (ex. API docs).
* Topics/Discussion (Understanding Oriented):
  Human-friendly explanation of what exists in Geoxarray and why things are
  the way they are in Geoxarray. These will generally not include actual code
  except for simple examples or to make a point. These should leverage the
  other sections of documentation to provide more low-level and hands-on
  information.

The FAQ document is left for anything that doesn't quite fit into any of the
above sections.