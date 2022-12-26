Comparisons
===========


Comparing Panel and Bokeh
-------------------------

Panel and Bokeh can both be used to create dashboards in Python, but are intended for different uses and different audiences:

- Panel is based on the internal layout and server components of Bokeh, while adding full bidirectional communication support for usage in Jupyter, making the same code fully usable in both notebook and server contexts so that it need not be rewritten for different purposes.

- Panel does not depend on any of Bokeh's plotting, and it can be used equally well with plots from a very wide variety of sources. To use such plots with Bokeh directly would require significant custom coding.

- Bokeh focuses on providing lower-level primitives that can be used to create any dashboard with enough effort, while Panel focuses on making common data-science tasks and making typical types of apps easier.



Comparing Panel and Dash
------------------------

Panel and Dash can both be used to create dashboards in Python, but take very different approaches:

- Panel provides full, seamless support for usage in Jupyter notebooks, making it simple to add controls and layouts wherever they are needed in a workflow, without necessarily building up to any particular shareable app. Dash is focused almost exclusively on standalone dashboards, though there are some workarounds available for using Dash in notebooks.

- Panel focuses on helping Python users create apps and dashboards using Python, with a concise and expressive Pythonic syntax. Dash reveals more of the underlying HTML and CSS details, which is useful for customization but can be distracting during the data-exploration phase of a project.

- Panel is plotting-library agnostic, fully supporting a wide range of Python libraries out of the box, including Plotly. Dash has full support for Plotly but only limited support for other plotting libraries, using separate extension packages.

- Dash dashboards store all of their per-user session state in the client (i.e., the browser), while Panel allows per-user, per-session state in both the server and the client, synchronizing between the two if needed. This difference has important implications:

  * Dash's approach is more highly scalable in some cases, allowing many simultaneous client sessions without necessarily using up resources on the server for each new client.

  * Panel's approach makes it easy to do server-side caching of intermediate computations for each user, which can make complex processing pipelines much more responsive. For instance, when used with a Datashader pipeline where the server renders an image from data that is never transmitted to the client, only the stages that have actually changed need to be re-run when a user interacts with the plot, making rendering changes like selecting a colormap almost instantaneous because the already aggregated data can be reused. With Dash, the server does not retain a copy of the intermediate data in such a pipeline, so when a new request comes in, it has to recompute each of the stages even when the data involved has not changed.  The `Datashader example dashboard <https://examples.pyviz.org/datashader_dashboard/dashboard.html>`__ shows how to use this intermediate-value caching to provide the fastest possible updates for a given user action, only re-running the computation actually needed to satisfy the request, re-using cached values stored on the server when appropriate.


Comparing Panel and ipywidgets
------------------------------

Both Panel and ipywidgets (aka Jupyter Widgets) allow Python users to work with custom widgets and create apps and dashboards from Python, both in Jupyter notebooks and in standalone servers (when paired with Voila). But Panel and ipywidgets are based on different, independently developed technologies for doing so, with some implications:

- Panel is based on Bokeh widgets, which were developed separately from the Jupyter ecosystem, and designed from the start for standalone deployments. Jupyter widgets, as the name suggests, were first developed specifically for the notebook environment, and only relatively recently (in 2019) adapted for standalone deployment (see Voila, below). Nowadays, both technologies have evolved to be well suited to both Jupyter and server contexts, but their different histories are still visible in the types of examples you typically see and in support for less-common operations for each library.

- ipywidgets expose more of the underlying HTML/CSS styling options, allowing them to be customized more heavily than Bokeh widgets currently allow.

- Panel widgets support easy embedding into static HTML pages for exporting notebooks, while ipywidgets require a separate and cumbersome `"embed widget state" <https://ipywidgets.readthedocs.io/en/latest/embedding.html>`__ operation to copy state from Python into the web page source. Panel widgets are thus easier to use for HTML reports, documentation (e.g. with Sphinx), and other cases where the output needs to be readable or usable without a running Python process.

- Where appropriate, Panel supports separating your scientific/engineering/business logic from your GUI implementation, allowing you to declare information that is used to make widgets in a way that is independent of any particular GUI toolkit, web packages, browser, or any other fast-changing technology. Specifically, Panel widgets build on the `Param <https://param.pyviz.org>`__ library that allows capturing the arguments and parameters of functions and classes independently of how the user may later provide or adjust those values. Param lets you specify the name, type, docstring, and range of valid values in a generic way that has no dependencies on any GUI library (or any other library) and allows validating user input in general, not just for a specific dashboard app. Once the parameters have been declared, the code can be used for command-line applications, servers, batch jobs, or (with Panel) generating live, active widgets automatically with no further customization needed to build an app. Param has been in continuous use by multiple libraries since 2003, across many generations of GUI toolkits, and can be expected to adapt to future toolkits as they become available without needing changes to your own domain-specific codebase. Via Param, Panel can thus integrate into a large, long-lived codebase that is used in a variety of different ways at any one time or over its lifetime, such as a simulator or modeling tool, domain-specific analysis libraries, automated processing pipelines, and so on, without ever needing the code to be rewritten or having the GUI code drift out of sync with the business/scientific logic. ipywidgets were designed primarily for the final application or dashboard usage, not for this full life cycle of research or analysis code.

- Panel widgets are reactive, allowing declarative specification of dependencies between code and widgets (or, more specifically, between code and the Param parameter values inside the widgets). This approach makes it possible to support directly accepting widget objects as arguments to Python code. That way, users never have to write explicit Python callbacks, yet the code will dynamically be executed as needed to respond to user interaction. This programming paradigm can provide highly responsive GUI applications with much less code and much simpler reasoning, as illustrated in the `Datashader widget dashboard <https://anaconda.org/jbednar/dashboard_barewidgets/notebook>`__.

- As of 9/2020, both types of widgets are now fully interoperable; you can use Panel or Bokeh widgets and panes in an ipywidgets-based app using `jupyter_bokeh <https://github.com/bokeh/jupyter_bokeh>`_ and you can use ipywidgets in a Panel or Bokeh app using `ipywidgets_bokeh <https://github.com/bokeh/ipywidgets_bokeh>`_.  So in practice, you can now mix and match content from either ecosystem as needed, choosing your "native" ecosystem based on other factors like deployment options (see below).



Comparing Panel and Voila
-------------------------

Voila is a technology for deploying Jupyter notebooks (with or without Panel code) as standalone web pages backed by Python. Voila is thus one way you can deploy your Panel apps, your ipywidgets-based apps, or any other content visible in a Jupyter notebook (including multiple languages, like R or C++). Voila is an alternative to the Bokeh Server component that is available through ``panel serve``; Panel works with either one, and you can deploy with *either* Bokeh Server (panel serve) or Voila. To serve a Panel app with Voila, just install `jupyter_bokeh <https://github.com/bokeh/jupyter_bokeh>`__ and do ``pn.ipywidget(panel_obj)``, which makes an ipywidget out of your Panel object that Voila (or Jupyter itself) can then display and let you interact with.

Similarly, widgets and plots that use ipywidgets, such as ipyvolume, ipyleaflet, or bqplot, can be used in your Panel app and deployed with Bokeh/Panel Server without needing Voila, as long as you have installed `ipywidgets_bokeh <https://github.com/bokeh/ipywidgets_bokeh>`_.

So, how do you choose between using Voila or Bokeh server if you are using Panel objects? Both servers are based on Tornado under the hood, but they differ in the fact that Jupyter will launch a new Python kernel for each user, while the Bokeh server can serve multiple users on the same process. This subtle difference has two major implications:

1. The per-user overhead for an app is much lower for Bokeh Server than for Voila. Once the relevant libraries are imported, there is only a tiny bit of overhead for creating each new user session. The Jupyter server, on the other hand, always launches an entirely new process per user session, with all the overhead that entails. For a session that imports nothing but pandas and matplotlib the per-user overhead is 75 MB (as of 10/2019), which increases for more complex environments, limiting the number of users a Voila server can handle for a given application.

2. Since a Bokeh server shares a single process for multiple sessions, data or processing can also be shared between the different sessions where appropriate. Such sharing makes it possible to further reduce the memory footprint of a Bokeh-Server app, to make it practical to support larger numbers of users and to provide faster startup or data-access times. (Dash goes even further, with no state stored per user, which is the opposite extreme from Voila, with the opposite issues and downsides.)

The other major difference between Bokeh Server and Voila is the way they process notebook files. Voila is built directly on the notebook format, though it also provides some support for bare Python files. By default, all output in the notebook (including Markdown cells) is included in the rendered Voila app, which has the benefit that existing notebooks can be served as apps *unchanged*. While that approach can be useful to get a quick set of plots, an existing notebook is unlikely to be organized and formatted in a way that forms a coherent dashboard, so in practice a notebook will need to be rewritten (suppressing most of the markdown and cell outputs, rearranging other cell outputs, etc.) before it will make a good Voila dashboard. In practice, you will then end up with two copies of the notebook: one optimized to be a narrative, storytelling notebook with a series of cells, and another organized as a dashboard. Or you can write a template to select only the cells you want in the dashboard and rearrange them, but then you need to maintain both the notebook and the template separately.

Panel takes a different approach, in that output from a notebook cell needs to be explicitly wrapped in a Panel object and marked as being "servable"; cell outputs and Markdown cells by default are shown only in the notebook, and not with ``panel serve``. Panel in fact entirely ignores the fact that your notebook is organized into cells; it simply processes all the cells as Python code, and serves all the items that ended up being marked "servable". Although this approach means editing the original notebook before you can see a dashboard, it makes it fully practical for the same notebook to serve both an exploratory or storytelling purpose (in Jupyter) and act as a dashboard deployment (of a designated subset of the functionality). The Panel developers very often use this functionality to provide detailed documentation for any given panel, with the cell-by-cell output showing the dataset, intermediate steps, interesting features, and how-tos, while the final deployed dashboard focuses on the final result, with the content in each case organized to best suit its purpose.


Comparing Panel and streamlit
-----------------------------

streamlit is an alternative to all of the above packages. Like Jupyter, streamlit provides an interactive, incremental way to build apps. streamlit works with Python text files written in a separate editor, while Jupyter uses a web-based notebook cell editor. Although a web-based editor makes it simple to work locally on remote files, using a local Python text file allows users to maximize their productivity by choosing their own favorite editor. Dash, Panel, and Bokeh all also support bare Python files developed in a local editor, and like streamlit they can all also watch that file and automatically re-run the file when you change it in the editor (e.g. for Panel or Bokeh, launch ``bokeh serve file.py --dev`` to watch the Python file and re-launch the served app on any changes).

Streamlit's key difference from those other tools is that with streamlit, the entire Python source file is effectively re-run *every time a widget changes value*, which has the advantage of not allowing confusing out-of-order execution of notebook cells, and also can make it simpler to reason about state in general. However, for this approach to be practical, it requires all lengthy computations to be made cacheable, which is not always straightforward and can introduce its own highly complicated reasoning about state. Moreover, the streamlit approach has similar downsides as for Dash's lack of server-side state, in that it becomes difficult to generate responsive apps for complex situations that need a precise mapping between a widget event and a specific small bit of Python code. Panel thus has better support for fully reactive applications, where each widget or component of a plot is explicitly and specifically tied to a bit of computation, re-running only the tiniest bit of code that is needed for that particular action.

Another major difference is that Panel, in contrast to streamlit, fully supports Jupyter notebooks, for when you wish to preserve a series of text/code/output steps as an exploratory record, whether to document a workflow for later reproducibility, to tell a story about data, or for any other approach where having individual outputs per cell is useful. Thus Panel does not require you to make a binary switch between "exploring some data" or "telling a story" and "developing an app"; it simply lets you use widgets and layouts whenever they are useful or appropriate, without ever having a cost to switch between such activities. Of course, Panel does not *require* Jupyter, but because it supports Jupyter fully it is usable in a wide range of situations for which streamlit is not designed.

Overall, Panel can be used in a much wider range of applications than streamlit, including exploratory data analysis and capturing a reproducible workflow in a Jupyter notebook, developing a simple streamlit-like app, or developing complex, multi-page responsive apps, all without having to switch frameworks or learn a new set of tools. Panel thus supports the entire life cycle of data science, engineering, or scientific artifacts, not just a narrow task of developing a specific type of simple app.
