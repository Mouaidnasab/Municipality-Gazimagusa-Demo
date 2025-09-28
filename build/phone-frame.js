/* phone-frame.js */
(function(){
  var DESKTOP_BREAKPOINT = 768; // >= is desktop

  function isEmbedded(){
    return new URLSearchParams(window.location.search).has('embed');
  }

  function ensureMobileViewport(){
    var vp = document.querySelector('meta[name="viewport"]');
    if(!vp){
      vp = document.createElement('meta');
      vp.name = 'viewport';
      document.head.appendChild(vp);
    }
    vp.setAttribute('content','width=device-width, initial-scale=1.0, maximum-scale=1.0');
  }

  function buildPhoneShell(){
    document.documentElement.style.height = 'auto';
    document.body.classList.add('__phone-stage');

    var frame = document.createElement('div');
    frame.className = 'phone-frame';

    var screen = document.createElement('div');
    screen.className = 'phone-frame__screen';

    var url = new URL(window.location.href);
    url.searchParams.set('embed','1'); // stop recursion

    var iframe = document.createElement('iframe');
    iframe.className = 'phone-frame__iframe';
    iframe.src = url.toString();
    iframe.title = 'Mobile preview';

    screen.appendChild(iframe);
    frame.appendChild(screen);

    document.body.innerHTML = '';
    document.body.appendChild(frame);

    function fit(){
      var cs = getComputedStyle(document.documentElement);
      var fw = parseFloat(cs.getPropertyValue('--frame-w')) || 460;
      var fh = parseFloat(cs.getPropertyValue('--frame-h')) || 900;
      var minS = parseFloat(cs.getPropertyValue('--min-scale')) || 0.6;
      var maxS = parseFloat(cs.getPropertyValue('--max-scale')) || 1.0;
      var pad = 32;
      var s = Math.min((window.innerWidth - pad)/fw, (window.innerHeight - pad)/fh);
      s = Math.max(Math.min(s, maxS), minS);
      frame.style.transform = 'scale('+s+')';
    }
    window.addEventListener('resize', fit, {passive:true});
    fit();
  }

  function run(){
    var isDesktop = Math.max(window.innerWidth, screen.width) >= DESKTOP_BREAKPOINT;

    if (!isDesktop) {
      // Real mobile — leave page alone
      return;
    }

    if (isEmbedded()) {
      // Inside iframe — behave like a real phone
      ensureMobileViewport();
      return;
    }

    // Outer desktop shell
    buildPhoneShell();
  }

  if (document.readyState === 'complete') run();
  else window.addEventListener('load', run);
})();
