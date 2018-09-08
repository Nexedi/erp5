// Type definitions for RenderJS

// XXX this is work in progress.

declare class Gadget {
    /**
     *  RenderJs gadget class.
     */
    constructor();

    /**
     * `ready`: define a function to be called when gadget is ready
     * XXX (gadget: Gadget) ? isn't it a gadget *instance* ?
     *
     * @params f function to call when gadget is ready. XXX this function returns a queue and gadget is ready once the queue is "empty" / "resolved" ?
     */
    ready(f: (gadget: Gadget) => RSVP.Queue): Gadget;

    /**
     * `declareService`: declare a service.
     *
     * @params serviceName name of the service
     * @params service function implementing the service logic.
     */
    declareService(serviceName: String, service: (gadget: Gadget) => RSVP.Queue): Gadget;
    declareJob(serviceName: String, service: (gadget: Gadget) => RSVP.Queue): Gadget;

    declareMethod(methodName: String, method: (gadget: Gadget) => RSVP.Queue): Gadget;
    declareAcquiredMethod(localMethodName: String, parentMethodName: String): Gadget;

}

/**
 * Initialize this gadget.
 */
declare function rJS(window: Window): Gadget;
