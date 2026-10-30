/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareMethod('getDefinition', function () {
      return {
        name: "execution_plan",
        executionMode: "sequential",
        description: "USE THIS ONLY WHEN THE USER EXPLICITLY ASKS for a plan or a checklist " +
          "(eg. \"make a plan first\", \"track the steps\"). Otherwise do not call it: just do the work " +
          "with the other tools. Shows the user an ordered checklist of steps towards a goal, live in " +
          "your current chat message. Two commands: \"set\" creates or completely replaces the plan " +
          "(every step back to \"pending\" - mark finished steps \"done\" again afterwards), and " +
          "\"update_step\" changes one step's status with an optional note. Once a turn finishes, its " +
          "final checklist stays attached to it, so a later \"set\" for a new goal does not hide it. " +
          "Never call \"set\" just to test the tool while a plan is in progress: it replaces that plan " +
          "and the step indices you were using become invalid.",
        parameters: {
          type: "object",
          properties: {
            command: { type: "string", "enum": ["set", "update_step"] },
            goal: { type: "string", description: "Required for \"set\": the overall goal / success condition this plan works towards." },
            step_list: {
              type: "array",
              description: "Required for \"set\": ordered list of steps.",
              items: {
                type: "object",
                properties: { title: { type: "string" } },
                required: ["title"]
              }
            },
            index: { type: "integer", description: "Required for \"update_step\": 0-based index of the step in the current plan's step_list." },
            status: { type: "string", "enum": ["pending", "in_progress", "done", "failed", "skipped"], description: "Required for \"update_step\"." },
            note: { type: "string", description: "Optional, for \"update_step\": dry-run prediction, real result, or reason for failure/skip." }
          },
          required: ["command"]
        }
      };
    })
    .declareMethod('render', function () {
      return;
    })
    .declareMethod('execute', function (args) {
      var gadget = this, step;
      function renderPlanText(plan) {
        if (!plan) {
          return "(no execution plan set)";
        }
        return "Goal: " + plan.goal + "\n" + plan.step_list.map(function (step, i) {
          return i + ". [" + step.status + "] " + step.title + (step.note ? " - " + step.note : "");
        }).join("\n");
      }

      if (args.command === "set") {
        gadget.execution_plan = {
          goal: args.goal || "",
          step_list: (args.step_list || []).map(function (step_spec) {
            return { title: step_spec.title, status: "pending", note: "" };
          })
        };
        return { content: renderPlanText(gadget.execution_plan), execution_plan: gadget.execution_plan };
      }
      if (args.command === "update_step") {
        if (!gadget.execution_plan) {
          return "ERROR: no execution plan has been set yet - call execution_plan with command \"set\" first.";
        }
        step = gadget.execution_plan.step_list[args.index];
        if (!step) {
          return "ERROR: no step at index " + args.index + " in the execution plan that is " +
            "CURRENTLY active (it has " + gadget.execution_plan.step_list.length + " step(s), valid indices " +
            "0-" + (gadget.execution_plan.step_list.length - 1) + "). If you did not expect this, it is likely " +
            "because \"set\" was called again since you last checked (e.g. to test the tool) and " +
            "replaced the plan you meant to update - here is what is actually active right now, " +
            "re-sync your step indices against it:\n" + renderPlanText(gadget.execution_plan);
        }
        step.status = args.status;
        step.note = args.note || "";
        return { content: renderPlanText(gadget.execution_plan), execution_plan: gadget.execution_plan };
      }
      return "ERROR: unknown command \"" + args.command + "\" - must be \"set\" or \"update_step\".";
    });
}(window, rJS, RSVP));
