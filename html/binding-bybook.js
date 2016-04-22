// @(#) $Id: binding.js 560 2005-12-14 21:57:35Z dom $

// Run code when the page loads.  From
// http://simon.incutio.com/archive/2004/05/26/addLoadEvent
function addLoadEvent(func) {
  var oldonload = window.onload;
  if (typeof window.onload != 'function') {
    window.onload = func;
  } else {
    window.onload = function() {
      oldonload();
      func();
    }
  }
}

// Set up functions to run when events occur.
function installHandlers() {
  if (!document.getElementById) return;

  var isbn = document.getElementById('isbn');
  if (isbn) {
      // When the user leaves this element, call the server.
      isbn.onchange = function() {
          loadBook(['isbn'], ['bookinfo']);
          return true;          // Continue with default action.
      }
  }
}

addLoadEvent( installHandlers );
