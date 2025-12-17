/**
 * Code to be injected inside the iframe
 * This code needs to be added to the generated preview website HTML for cross-origin communication
 *
 * Placement: In the <head> or before the closing </body> tag of the generated HTML
 */

(function() {
  // Track history index
  let historyIdx = 0;

  // Listen for messages from parent page
  window.addEventListener('message', (event) => {
    // Optional: Verify message origin
    // if (event.origin !== 'http://localhost:5173') return;

    const message = event.data;

    // Handle goBack command
    if (message === 'goBack') {
      window.history.back();
    }

    // Handle goForward command
    if (message === 'goForward') {
      window.history.forward();
    }
  });

  // Listen for popstate events (browser back/forward)
  window.addEventListener('popstate', (event) => {
    // Send popstate event to parent page
    window.parent.postMessage({
      type: 'popstate',
      data: {
        idx: event.state?.idx || historyIdx,
        state: event.state
      }
    }, '*');
  });

  // Intercept pushState to monitor route changes
  const originalPushState = window.history.pushState;
  window.history.pushState = function(...args) {
    historyIdx++;

    // Call original pushState
    const result = originalPushState.apply(this, args);

    // Send custom pushstate event to parent page
    window.parent.postMessage({
      type: 'custom-pushstate',
      data: { idx: historyIdx }
    }, '*');

    // Dispatch custom event for internal iframe usage
    window.dispatchEvent(new CustomEvent('custom-pushstate'));

    return result;
  };

  // Intercept replaceState
  const originalReplaceState = window.history.replaceState;
  window.history.replaceState = function(...args) {
    const result = originalReplaceState.apply(this, args);

    // Optional: Send replaceState event
    window.parent.postMessage({
      type: 'custom-replacestate',
      data: { idx: historyIdx }
    }, '*');

    return result;
  };

  console.log('iframe-integration.js loaded');
})();
