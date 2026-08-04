/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareMethod('getDefinition', function () {
      return {
        name: "execution_plan",
        description: "Create, replace or update your execution plan: an ordered checklist of steps " +
          "working towards a stated goal, shown to the user as a live checklist right in your current " +
          "chat message. Two commands: \"set\" (create or completely replace the plan - call this first " +
          "for any non-trivial multi-step request, before doing any work, and call it again with the " +
          "FULL, updated step list whenever you revise the plan - e.g. after reasoning through a step (a " +
          "\"dry run\": predict what would happen without actually doing it yet) reveals the plan needs " +
          "to change; every \"set\" replaces the checklist shown in the CURRENT message with a new one - " +
          "fresh steps, every status reset to \"pending\" - re-mark already-finished steps as \"done\" " +
          "again afterwards with \"update_step\" if they still are) and \"update_step\" (update one step's " +
          "status and an optional note - e.g. a dry-run prediction before actually doing the step, or the " +
          "real outcome afterwards - call it after reasoning through or actually executing every step). " +
          "Nothing is lost: once a turn finishes, its final checklist state is kept permanently attached " +
          "to it, so calling \"set\" again later (in a new message, for a new/different goal) never " +
          "overwrites or hides the earlier one - scrolling up still shows exactly how each past plan " +
          "ended up. USE THIS WHEN: the request needs several distinct actions, or asks you to create " +
          "and iteratively improve a plan until some condition holds. DO NOT USE for a single-step " +
          "request a direct reply or tool call already answers. WARNING: never call \"set\" just to " +
          "test/demonstrate the tool while a real plan is still in progress - it immediately replaces " +
          "that plan, so every step index you were tracking (for \"update_step\") becomes invalid. If you " +
          "need to sanity-check this tool, do it only when no real plan is active, or restate the real " +
          "plan's steps again afterwards.",
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
      var gadget = this, plan, step;
      if (args.command === "set") {
        plan = {
          goal: args.goal || "",
          step_list: (args.step_list || []).map(function (step_spec) {
            return { title: step_spec.title, status: "pending", note: "" };
          })
        };
        gadget.execution_plan = plan;
        return { content: window.ChatToolCommon.renderPlanText(plan), execution_plan: plan };
      }
      if (args.command === "update_step") {
        plan = gadget.execution_plan;
        if (!plan) {
          return "ERROR: no execution plan has been set yet - call execution_plan with command \"set\" first.";
        }
        step = plan.step_list[args.index];
        if (!step) {
          return "ERROR: no step at index " + args.index + " in the execution plan that is " +
            "CURRENTLY active (it has " + plan.step_list.length + " step(s), valid indices " +
            "0-" + (plan.step_list.length - 1) + "). If you did not expect this, it is likely " +
            "because \"set\" was called again since you last checked (e.g. to test the tool) and " +
            "replaced the plan you meant to update - here is what is actually active right now, " +
            "re-sync your step indices against it:\n" + window.ChatToolCommon.renderPlanText(plan);
        }
        step.status = args.status;
        step.note = args.note || "";
        gadget.execution_plan = plan;
        return { content: window.ChatToolCommon.renderPlanText(plan), execution_plan: plan };
      }
      return "ERROR: unknown command \"" + args.command + "\" - must be \"set\" or \"update_step\".";
    });
}(window, rJS, RSVP));
