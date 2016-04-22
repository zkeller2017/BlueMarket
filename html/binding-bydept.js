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

  var dept = document.getElementById('dept');
  if (dept) {
      // When the user leaves this element, call the server.
      dept.onchange = function() {
          loadDept(['dept'], ['course']);
          return true;          // Continue with default action.
      }
  }

  var course = document.getElementById('course');
  if (course) {
      // When the user leaves this element, call the server.
      course.onchange = function() {
          loadCourse(['course'], ['ads']);
          return true;          // Continue with default action.
      }
  }
}

addLoadEvent( installHandlers );
