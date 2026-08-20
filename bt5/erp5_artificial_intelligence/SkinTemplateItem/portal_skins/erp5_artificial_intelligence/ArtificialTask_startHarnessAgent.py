import json
artificial_task = context

if artificial_task.getSimulationState() != 'processing':
  artificial_task.start()
artificial_task.activate(activity='SQLQueue').ArtificialTask_harnessAgent()

return json.dumps({"started": True})
