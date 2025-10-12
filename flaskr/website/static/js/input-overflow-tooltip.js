/**
 * Input Overflow Tooltip Handler
 * File: input-overflow-tooltip.js
 * Automatically adds tooltips to input fields and table cells with truncated text
 * for the ASL Pharmacy Simulation Tool
 */

(function () {
  "use strict";

  /**
   * Check if an element's content is truncated
   */
  function isTextTruncated(element) {
    // For input fields, check if scrollWidth exceeds clientWidth
    if (element.tagName === "INPUT" || element.tagName === "SELECT") {
      return element.scrollWidth > element.clientWidth;
    }

    // For regular elements
    if (
      element.scrollWidth > element.clientWidth ||
      element.scrollHeight > element.clientHeight
    ) {
      return true;
    }

    return false;
  }

  /**
   * Add tooltip to element if text is truncated
   */
  function addTooltipIfTruncated(element) {
    // Skip if element already has a title
    if (
      element.hasAttribute("title") ||
      element.hasAttribute("data-bs-original-title")
    ) {
      return;
    }

    let textContent = "";

    // Get text content based on element type
    if (element.tagName === "INPUT") {
      textContent = element.value;
    } else if (element.tagName === "SELECT") {
      const selectedOption = element.options[element.selectedIndex];
      textContent = selectedOption ? selectedOption.text : "";
    } else {
      textContent = element.textContent || element.innerText;
    }

    // Only add tooltip if text exists and is truncated
    if (textContent.trim() && isTextTruncated(element)) {
      element.setAttribute("title", textContent.trim());

      // If Bootstrap tooltips are available, initialize them
      if (typeof bootstrap !== "undefined" && bootstrap.Tooltip) {
        new bootstrap.Tooltip(element, {
          trigger: "hover",
          placement: "top",
          boundary: "window",
        });
      }
    }
  }

  /**
   * Remove tooltip if text is no longer truncated
   */
  function removeTooltipIfNotTruncated(element) {
    if (!isTextTruncated(element)) {
      element.removeAttribute("title");
      element.removeAttribute("data-bs-original-title");

      // Dispose Bootstrap tooltip if it exists
      if (typeof bootstrap !== "undefined" && bootstrap.Tooltip) {
        const tooltipInstance = bootstrap.Tooltip.getInstance(element);
        if (tooltipInstance) {
          tooltipInstance.dispose();
        }
      }
    }
  }

  /**
   * Process all input fields and add tooltips where needed
   */
  function processInputFields() {
    const selectors = [
      'input[type="text"].form-control',
      'input[type="email"].form-control',
      'input[type="tel"].form-control',
      "input[readonly].form-control",
      "select.form-select",
      ".form-control-sm",
      ".form-select-sm",
    ];

    selectors.forEach((selector) => {
      document.querySelectorAll(selector).forEach((element) => {
        addTooltipIfTruncated(element);
      });
    });
  }

  /**
   * Process table cells and add tooltips where needed
   */
  function processTableCells() {
    document.querySelectorAll(".table td").forEach((cell) => {
      addTooltipIfTruncated(cell);
    });
  }

  /**
   * Process scenario names and other potentially long text
   */
  function processLongTextElements() {
    const selectors = [
      ".scenario-name",
      ".scenario-name a",
      ".patient-name",
      ".user-name",
      ".fw-semibold",
      ".badge",
    ];

    selectors.forEach((selector) => {
      document.querySelectorAll(selector).forEach((element) => {
        addTooltipIfTruncated(element);
      });
    });
  }

  /**
   * Handle input field changes
   */
  function handleInputChange(event) {
    const element = event.target;

    // Remove old tooltip
    removeTooltipIfNotTruncated(element);

    // Add new tooltip if needed
    setTimeout(() => {
      addTooltipIfTruncated(element);
    }, 100);
  }

  /**
   * Handle window resize
   */
  function handleResize() {
    // Reprocess all elements on resize
    processInputFields();
    processTableCells();
    processLongTextElements();
  }

  /**
   * Initialize mutation observer to watch for dynamic content
   */
  function initMutationObserver() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
          // Process newly added nodes
          setTimeout(() => {
            processInputFields();
            processTableCells();
            processLongTextElements();
          }, 200);
        }
      });
    });

    // Observe the entire document body for changes
    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  /**
   * Add click-to-copy functionality for truncated text
   */
  function addClickToCopy() {
    document.addEventListener("dblclick", function (event) {
      const element = event.target;

      // Only for input fields with truncated text
      if (
        (element.tagName === "INPUT" || element.tagName === "TD") &&
        element.hasAttribute("title")
      ) {
        const textToCopy = element.getAttribute("title");

        // Try to copy to clipboard
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard
            .writeText(textToCopy)
            .then(() => {
              // Show feedback
              const originalTitle = element.getAttribute("title");
              element.setAttribute("title", "Copied to clipboard!");

              // Restore original title after 2 seconds
              setTimeout(() => {
                element.setAttribute("title", originalTitle);
              }, 2000);
            })
            .catch((err) => {
              console.error("Failed to copy text:", err);
            });
        }
      }
    });
  }

  /**
   * Initialize all functionality
   */
  function init() {
    // Wait for DOM to be ready
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", init);
      return;
    }

    // Initial processing
    processInputFields();
    processTableCells();
    processLongTextElements();

    // Add event listeners for input changes
    document.addEventListener("input", handleInputChange);
    document.addEventListener("change", handleInputChange);

    // Handle window resize with debouncing
    let resizeTimeout;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(handleResize, 250);
    });

    // Initialize mutation observer for dynamic content
    initMutationObserver();

    // Add double-click to copy functionality
    addClickToCopy();

    // Reprocess after a short delay to catch any dynamically loaded content
    setTimeout(() => {
      processInputFields();
      processTableCells();
      processLongTextElements();
    }, 1000);
  }

  // Start initialization
  init();
})();

/**
 * Utility function to manually add tooltips to specific elements
 * Can be called from other scripts if needed
 */
window.ASLTooltipUtils = {
  addTooltip: function (element) {
    if (element && typeof element.getAttribute === "function") {
      const isInputOrSelect =
        element.tagName === "INPUT" || element.tagName === "SELECT";
      const textContent = isInputOrSelect ? element.value : element.textContent;

      if (textContent && textContent.trim()) {
        element.setAttribute("title", textContent.trim());

        if (typeof bootstrap !== "undefined" && bootstrap.Tooltip) {
          new bootstrap.Tooltip(element, {
            trigger: "hover",
            placement: "top",
          });
        }
      }
    }
  },

  removeTooltip: function (element) {
    if (element) {
      element.removeAttribute("title");
      element.removeAttribute("data-bs-original-title");

      if (typeof bootstrap !== "undefined" && bootstrap.Tooltip) {
        const tooltipInstance = bootstrap.Tooltip.getInstance(element);
        if (tooltipInstance) {
          tooltipInstance.dispose();
        }
      }
    }
  },
};
