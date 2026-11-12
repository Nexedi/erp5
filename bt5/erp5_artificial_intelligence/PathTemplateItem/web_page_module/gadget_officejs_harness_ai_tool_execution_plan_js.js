/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareMethod('getDefinition', function () {
      return {
        name: "execution_plan",
        executionMode: "sequential",
        description: "Show the user a checklist of the steps towards a goal, updated live in your " +
          "answer. Use it ONLY when the user asks for a plan or a checklist (eg. \"make a " +
          "plan first\"): otherwise just do the work. \"set\" creates the plan, or replaces " +
          "it with all its steps pending: call it again only for a new goal. \"update_step\" " +
          "changes the status of one step, with an optional note.",
        parameters: {
          type: "object",
          properties: {
            command: { type: "string", "enum": ["set", "update_step"] },
            goal: { type: "string", description: "For \"set\": the goal of the plan." },
            step_list: {
              type: "array",
              description: "For \"set\": the steps, in order.",
              items: {
                type: "object",
                properties: { title: { type: "string" } },
                required: ["title"]
              }
            },
            index: { type: "integer", description: "For \"update_step\": index of the step, from 0." },
            status: {
              type: "string",
              "enum": ["pending", "in_progress", "done", "failed", "skipped"],
              description: "For \"update_step\"."
            },
            note: { type: "string", description: "For \"update_step\", optional: the result, or why the step failed or was skipped." }
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
