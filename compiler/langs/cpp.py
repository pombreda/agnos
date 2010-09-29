from contextlib import contextmanager


class Stmt(object):
    def __init__(self, text, *args, **kwargs):
        if text:
            stripped = text.strip()
            default_suffix = "" if stripped.startswith("#") or stripped.endswith(":") else ";"
        else:
            default_suffix = ";" 
        self.suffix = kwargs.pop("suffix", default_suffix)
        if kwargs:
            raise TypeError("invalid keyword arguments %r" % (kwargs.keys(),))
        if args:
            text = text.format(*args)
        self.text = text
    
    def render(self):
        return [self.text + self.suffix]

EmptyStmt = Stmt("", suffix = "")

class Doc(object):
    def __init__(self, text, box = False, spacer = False):
        self.box = box
        self.spacer = spacer
        self.text = text
    
    def render(self):
        lines = ["// " + l for l in self.text.splitlines()]
        if self.box:
            lines.insert(0, "//" * 39)
            lines.append("//" * 39)
        elif self.spacer:
            lines.insert(0, "//")
            lines.append("//")
        return lines 


class Block(object):
    def __init__(self, text, *args, **kwargs):
        self.prefix = kwargs.pop("prefix", "{")
        token = text.split()[0] if text else None
        default_suffix = "};" if token in ["class", "struct", "enum"] else "}" 
        self.suffix = kwargs.pop("suffix", default_suffix)
        if kwargs:
            raise TypeError("invalid keyword arguments %r" % (kwargs.keys(),))
        self.title = Stmt(text, *args, suffix = "")
        self.children = []
        self.stack = []
    
    def _get_head(self):
        if not self.stack:
            return self
        else:
            return self.stack[-1]

    def sep(self, count = 1):
        for i in range(count):
            self._get_head().children.append(EmptyStmt)
    def doc(self, *args, **kwargs):
        self._get_head().children.append(Doc(*args, **kwargs))
    def stmt(self, *args, **kwargs):
        self._get_head().children.append(Stmt(*args, **kwargs))
    
    @contextmanager
    def block(self, *args, **kwargs):
        blk = Block(*args, **kwargs)
        self._get_head().children.append(blk)
        self.stack.append(blk)
        yield blk
        self.stack.pop(-1)
    
    def render(self):
        lines = self.title.render()
        if self.prefix:
            lines.append(self.prefix)
        for child in self.children:
            lines.extend("\t" + l for l in child.render())
        if self.suffix:
            lines.append(self.suffix)
        return lines


class Module(Block):
    def __init__(self):
        Block.__init__(self, None)
    def __enter__(self):
        return self
    def __exit__(self, t, v, tb):
        pass
    def render(self):
        lines = []
        for child in self.children:
            lines.extend(child.render())
        return "\n".join(lines)


if __name__ == "__main__":
    with Module() as m:
        BLOCK = m.block
        STMT = m.stmt
        SEP = m.sep
        
        STMT("using System")
        STMT("using System.Collections")
        STMT("using Thrift")
        SEP(2)
        with BLOCK("namespace t4"):
            with BLOCK("public class moshe"):
                STMT("private int x, y")
                SEP()
                with BLOCK("public moshe()"):
                    STMT("int x = 5")
                    STMT("int y = 6")
                SEP()
                with BLOCK("public ~moshe()"):
                    STMT("Dispose(false)")
    
    print m.render()




