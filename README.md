# ComfyUI-RyuuNoodles

Collection of one or more custom nodes for ComfyUI made mainly for personal use

## Switches with Fallback

Yes, there are already quite a few switch custom nodes. However I couldn't find any that would accept an/the second input being empty/None due to the connected node being bypassed or muted so I made these.
The Switch Any Fallback node is probably the best choice here <sub>although there's also an "Image" and "Latent" specific variant if you like the colors it gives the noodles i guess.</sub>
![Showcase for switches](assets/switches_showcase.png)
(True = input 1 will be chosen; False = input 2 will be attempted to be chosen, if fail due to input being None, output will use input 1 data and a message will be printed to console)
There's also a **Passthrough node** with the same functionality as the switch nodes, just without the boolean switch.
<sub>I briefly had the idea of allowing the user to add more switch nodes through a yaml with multiple inputs but I think this isn't good for reproducability/sharing the workflow.
A solution to still have a similar kind of thing is making a switch node that would allow a dynamic amount of inputs that increases using an option on the node or increases by 1 as inputs are being populated, however ComfyUI frontend updates are moving fast any changing how inputs work, and it seems like it breaks things like this (as can be seen on the Impact Pack Switch (Any) node as of writing, it doesn't create new inputs anymore) so I'm holding off working on that</sub>
