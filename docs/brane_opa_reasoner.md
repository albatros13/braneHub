The Brane reasoner is already designed to support different backends. 
The idea is that you can implement a "reasoner connector" object that processes calls from Brane, 
does reasoning (in whatever way the backend does) and then responds with a "ReasonerResponse" 
(which is just "OK" or "Violation" with an optional list of reasons).

This connector is written in Rust. However, Rust can also call C-libraries - 
or run any external executable, of course; so the main logic of the reasoner 
needn't be in Rust. For example, the eflint-haskell-reasoner connector simply 
receives questions to ask to the reasoner from Brane, translates them to input 
to a Haskell reasoner binary and parses its result. Depending on whether you 
already have some implementation of an Open Policy Agent lying around, 
you can perhaps attempt to wrap that in a similar way if it's not in Rust.

Based on what I understand from the Open Policy Agent's website, you'll probably have to:

1. Model a notion of Brane's workflow and the three types of questions in your policy language 
(questions are: 
* "Is this plan OK?", 
* "Are you OK executing this task in this workflow?" 
* "Are you OK providing this input to the user executing this task in this workflow?";

2. Figuring out how to run Open Policy Agent language (idk if it's called that xD) from Rust;
3. Writing a map of the Rust representation of the workflow & questions to however your policy likes it; ; and
4. Parsing the backend's output and mapping that back to the Rust values that the interface expects you to return.

Luckily, all the heavy lifting of doing actual communication with Brane is abstracted away; from your perspective, consulting the reasoner is just a function call. You'll get some arguments representing the input to the reasoner call, and you need to return the verdict of the reasoner.

The current list of implemented backends is found in https://github.com/BraneFramework/policy-reasoner/tree/main/lib/reasoners. For a minimal example, see the "no-op" reasoner (this file does the heavy lifting). Other backends can also be nice to see to get a feel for what realistic implementations look like.

In addition, I would also definitely ask Daniel to write the Rust-y part for you (;)), especially if you don't have a lot of Rust experience yourself. Regardless, the interface is a bit of a maze of traits and generics, so getting his help in understanding what you're looking at precisely would be very useful. You can also ask me, of course, although I am quite short on time nowadays so more than a meeting I can't arrange in the short term :)

But hopefully, this allows you to get started! Let me know how things go.