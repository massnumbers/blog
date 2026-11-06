function(el, x) {
  var map = this;
  var namespace = "http://www.w3.org/2000/svg";
  var prefix = el.id + "-outcome-";

  function stripePattern(svg, name, background, stripe) {
    var id = prefix + name;
    if (!svg.querySelector('[id="' + id + '"]')) {
      var defs = svg.querySelector("defs");
      if (!defs) {
        defs = document.createElementNS(namespace, "defs");
        svg.insertBefore(defs, svg.firstChild);
      }
      var pattern = document.createElementNS(namespace, "pattern");
      pattern.setAttribute("id", id);
      pattern.setAttribute("patternUnits", "userSpaceOnUse");
      pattern.setAttribute("width", "10");
      pattern.setAttribute("height", "10");
      pattern.setAttribute("patternTransform", "rotate(45)");
      [[background, "10"], [stripe, "1.5"]].forEach(function(values) {
        var rectangle = document.createElementNS(namespace, "rect");
        rectangle.setAttribute("width", values[1]);
        rectangle.setAttribute("height", "10");
        rectangle.setAttribute("fill", values[0]);
        pattern.appendChild(rectangle);
      });
      defs.appendChild(pattern);
    }
    return "url(#" + id + ")";
  }

  function decorate(layer) {
    var path = layer._path;
    if (path && path.ownerSVGElement) {
      if (path.classList.contains("outcome-r-to-d")) {
        path.style.fill = stripePattern(path.ownerSVGElement, "r-to-d", "#24589A", "#CB454A");
      } else if (path.classList.contains("outcome-d-to-r")) {
        path.style.fill = stripePattern(path.ownerSVGElement, "d-to-r", "#CB454A", "#24589A");
      }
    }
    if (layer.eachLayer) layer.eachLayer(decorate);
  }

  map.eachLayer(decorate);
  map.on("layeradd", function(event) { decorate(event.layer); });
}
