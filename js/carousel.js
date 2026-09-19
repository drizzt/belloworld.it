// Drag the carousel with a mouse.
//
// A touchscreen already swipes the strip and a trackpad already pans it. A
// mouse has no horizontal gesture at all, which left the carousel effectively
// stuck on a PC: the only way across was the scrollbar, or tabbing into the
// strip first and then using the arrow keys. Nobody does the second one.
//
// Vanilla and served from this site, like everything else the section loads.
// Without this file the strip still scrolls by touch, trackpad and scrollbar,
// so the page does not depend on it arriving.

document.querySelectorAll('.belli-carousel').forEach(function (strip) {
  var startX = 0;
  var startLeft = 0;
  var dragging = false;

  // The grab cursor is added here rather than in the stylesheet, so it only
  // ever promises a drag on a page where the drag actually works.
  strip.classList.add('is-draggable');

  strip.addEventListener('pointerdown', function (e) {
    // A mouse, and only its left button. A finger and a pen on a touchscreen
    // already pan the strip themselves, with momentum this does not have, and
    // scrolling it again from here would move it twice as far as the hand did.
    // A right or middle button press is not a drag: one opens a menu and the
    // other is the browser's own autoscroll.
    if (e.pointerType !== 'mouse' || e.button !== 0) return;

    dragging = true;
    startX = e.clientX;
    startLeft = strip.scrollLeft;

    // Snapping has to come off for the duration. Left on, it fights every
    // frame of the drag and yanks the strip back to the nearest slide.
    strip.classList.add('is-dragging');
    strip.setPointerCapture(e.pointerId);

    // Otherwise the browser starts its own drag of the image under the cursor.
    // Cancelling it also swallows the mousedown behind it, and with it the
    // click that would have focused the strip, so the focus is put back by
    // hand: it is what the arrow keys scroll once the mouse is done.
    e.preventDefault();
    // Firefox matches :focus-visible on a programmatic focus even when a mouse
    // press is what caused it, so every drag would leave the ring behind. The
    // class takes it off for the mouse only; the keydown below puts it back the
    // moment anyone actually steers with the keyboard.
    strip.classList.add('is-mouse-focus');
    strip.focus({ preventScroll: true });
  });

  strip.addEventListener('keydown', function () {
    strip.classList.remove('is-mouse-focus');
  });

  strip.addEventListener('blur', function () {
    strip.classList.remove('is-mouse-focus');
  });

  strip.addEventListener('pointermove', function (e) {
    if (!dragging) return;
    strip.scrollLeft = startLeft - (e.clientX - startX);
  });

  // The capture is not released here: the browser drops it by itself on
  // pointerup and pointercancel, and asking for a pointer that is already gone
  // is how that line throws instead of doing nothing.
  function release() {
    if (!dragging) return;
    dragging = false;
    // Putting snapping back settles the strip on whichever slide is nearest,
    // which is the whole reason it was worth turning off rather than dropping.
    strip.classList.remove('is-dragging');
  }

  strip.addEventListener('pointerup', release);
  strip.addEventListener('pointercancel', release);
});
