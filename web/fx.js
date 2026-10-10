(() => {
  const c = document.getElementById("field");
  if (!c) return;
  const ctx = c.getContext("2d");
  const dots = Array.from({length: 80}, () => ({
    x: Math.random(), y: Math.random(),
    r: 1 + Math.random() * 2.4,
    v: 0.12 + Math.random() * 0.4,
    a: 0.18 + Math.random() * 0.5
  }));
  function resize(){ c.width = innerWidth; c.height = innerHeight; }
  addEventListener("resize", resize); resize();
  (function tick(){
    ctx.clearRect(0, 0, c.width, c.height);
    for (const d of dots) {
      d.y -= d.v / c.height;
      if (d.y < 0) { d.y = 1; d.x = Math.random(); }
      ctx.beginPath();
      ctx.fillStyle = "rgba(94,224,160," + d.a + ")";
      ctx.arc(d.x * c.width, d.y * c.height, d.r, 0, 6.28);
      ctx.fill();
    }
    requestAnimationFrame(tick);
  })();
  document.querySelectorAll("article, .card").forEach(el => {
    el.addEventListener("mousemove", ev => {
      const b = el.getBoundingClientRect();
      const rx = ((ev.clientY - b.top) / b.height - 0.5) * -8;
      const ry = ((ev.clientX - b.left) / b.width - 0.5) * 10;
      el.style.transform = "perspective(700px) rotateX(" + rx + "deg) rotateY(" + ry + "deg) translateY(-2px)";
    });
    el.addEventListener("mouseleave", () => { el.style.transform = ""; });
  });
})();
