window.onload = function () {
  if (window.location.pathname === "/" || window.location.pathname === "") {
    window.location.replace("./docs/overview/");
  }
};
