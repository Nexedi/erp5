// Type definitions for renderjs 0.20.0
// Project: https://lab.nexedi.com/nexedi/renderjs
// Definitions by: Jerome Perrin <https://github.com/perrinjerome>
// Definitions: https://github.com/DefinitelyTyped/DefinitelyTyped (not yet)
// TypeScript Version: 2.4

// XXX needs nexedi RSVP patch loaded.

/**
 * A gadget state dict.
 */
interface GadgetState {
    [key: string]: any;
}

/**
 * Options to declared methods
 */
interface MethodOptions {
    /**
     * controls mutual exclusions of method calls.
     */
    mutex?: string;
}

/**
 * Options to declare a gadget.
 */
interface GadgetDeclarationOptions {
    /**
     * The local name of the gadget in declarer namespace
     */
    scope: string;

    /**
     * The sandbox type, can be iframe to render in an iframe or public to render in the
     * same window context.
     */
    sandbox: "public" | "iframe";

    /**
     * The element where to bind the gadget.
     */
    element: HTMLElement;
}

/**
 * RenderJS gadget instance
 */
declare class Gadget {
    /**
     * The current state of the gadget.
     * To mutate the state, use `changeState`.
     */
    public state: GadgetState;

    /**
     * Because declared methods will be added to the gadget class, the type declaration is loose.
     */
    [key: string]: any;

    /**
     * `declareGadget`: Declare a child gadget
     *
     * The parameters exactly correspond to those when declaring the gadget in HTML, with the addition of element, to specify an element to wrap the gadget in, rather than the default auto-generated <div>.
     *
     * @param gadgetURL the URL of the HTML page of the gadget.
     * @param options the gadget options
     */
    declareGadget(
        gadgetURL: string,
        options: GadgetDeclarationOptions
    ): RSVP.Queue<Gadget>;

    /**
     * `dropGadget`: Drop a child gadget.
     *
     * @param gadgetScope the scope of the previously declared gadget
     */
    dropGadget(gadgetScope: string): RSVP.Queue<Gadget>;

    /**
     * `getDeclaredGadget`: Get a previously declared child gadget
     *
     * Returns a child gadget instance, previously declared with `declareGadget`.
     *
     * @param gadgetScope the scope of the previously declared gadget
     */
    getDeclaredGadget(gadgetScope: string): RSVP.Queue<Gadget>;

    /**
     * `setState`: Set Initial State
     *
     * The gadget's state should be set once when initialising the gadget. The state should contain key/value pairs, but the state is just an ordinary JavaScript object with no hard restrictions.
     *
     * @param initialState the initial state.
     */
    setState(initialState: GadgetState): RSVP.Queue<void>;

    /**
     * `changeState`: Change State
     *
     * Change the state by passing in a new key-value pair, which only overwrites the keys provided in the changeState call, and only if the current and new values are different. All other keys remain unchanged.
     *
     * @param newState the changes made to the state.
     */
    changeState(newState: GadgetState): RSVP.Queue<void>;
}

/**
 *  RenderJs gadget class.
 */
interface GadgetKlass {
    /**
     * `onStateChange`: Change State Callback.
     *
     * @param handler function implementing the service logic.
     */
    onStateChange(
        handler: (
            this: Gadget,
            modification_dict: GadgetState
        ) => RSVP.Queue<any> | void
    ): GadgetKlass;

    /**
     * `ready`: define a function to be called when gadget is ready
     *
     * The ready handler is triggered automatically when all gadget dependencies have loaded.
     *
     * @param f function to call when gadget is ready.
     */
    ready(
        f: (this: Gadget, gadget?: Gadget) => RSVP.Queue<any> | void
    ): GadgetKlass;

    /**
     * `declareMethod`: Declare Method
     *
     * The ready handler is triggered automatically when all gadget dependencies have loaded.
     *
     * @param methodName name of the method
     * @param method function implementing the method logic.
     * @param methodOptions the options for this methods.
     */
    declareMethod(
        methodName: string,
        method: (this: Gadget, ...args: any[]) => any,
        methodOptions?: MethodOptions
    ): GadgetKlass;

    /**
     * `declareService`: Declare a service.
     *
     * Services automatically trigger as soon as the gadget is loaded into the DOM, and are usually used for event binding. There can be multiple declareService handlers, which all trigger simultaneously.
     *
     * @param service function implementing the service logic.
     */
    declareService(
        service: (this: Gadget) => RSVP.Queue<any> | Promise<any>
    ): GadgetKlass;

    /**
     * `declareJob`: Declare a job.
     *
     * Jobs manually trigger by being called, like an ordinary RenderJS method. However, calling a job cancels the last call of the job if it hasn't finished.   *
     *
     * @param jobName name of the job
     * @param service function implementing the job logic.
     */
    declareJob(
        jobName: string,
        job: (this: Gadget, ...args: any[]) => RSVP.Queue<any> | Promise<any>
    ): GadgetKlass;

    /**
     * `onEvent`: Bind Event.
     *
     * Jobs manually trigger by being called, like an ordinary RenderJS method. However, calling a job cancels the last call of the job if it hasn't finished.   *
     *
     * @param eventName name of the Event
     * @param eventHandler function implementing the logic.
     * @param useCapture same semantics as EventTarget.addEventListener
     * @param preventDefault XXX ?
     */
    onEvent(
        eventName: string,
        eventHandler: (this: Gadget, event?: Event) => RSVP.Queue<any>,
        useCapture?: boolean,
        preventDefault?: boolean | Promise<any> | void
    ): GadgetKlass;

    /**
     * `onLoop`: Loop.
     *
     * When the gadget is displayed, loop on the callback method in a service.
     * A delay can be configured between each loop execution.
     *
     * @param loopFunction the function to execute in the loop.
     * @param delay the delay between call, in seconds.
     */
    onLoop(loopFunction: (this: Gadget) => void, delay: number): GadgetKlass;

    /**
     * `allowPublicAcquisition`: Publish Method.
     *
     * Publish a method to allow children to acquire it.
     * Only methods passed into allowPublicAcquisition in a parent gadget can be acquired using declareAcquiredMethod in a child gadget.
     *
     * @param methodName name of the method
     * @param method function implementing the method logic.
     */
    allowPublicAcquisition(
        methodName: string,
        method: (this: Gadget, ...args: any[]) => any
    ): GadgetKlass;

    /**
     * `allowPublicAcquisition`: Publish Method.
     *
     * Acquire a method from a parent gadget, by passing the name of the published method as the first parameter and the name to call it locally as the second parameter.
     *
     * @param localMethodName name of the method as seen from this gadget instance.
     * @param parentMethodName name of the method on the parent gadget instance.
     */
    declareAcquiredMethod(
        localMethodName: string,
        parentMethodName: string
    ): GadgetKlass;
}

declare function rJS(window: Window): GadgetKlass;
