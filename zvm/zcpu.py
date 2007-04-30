#
# A class which represents the CPU itself, the brain of the virtual
# machine. It ties all the systems together and runs the story.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

from zopdecoder import ZOpDecoder

class ZCpuError(Exception):
    "General exception for Zcpu class"

class ZCpuOpcodeOverlap(ZCpuError):
    "Overlapping opcodes registered"

class ZCpuIllegalInstruction(ZCpuError):
    "Illegal instruction encountered"

class ZCpuUnimplementedInstruction(ZCpuError):
    "Unimplemented instruction encountered"

def declare_opcodes(func, opcodes, version=(1,2,3,4,5)):
    """Helper function used for declaring that a function implements
    some opcodes."""
    if hasattr(func, '_opcodes'):
        raise ZCpuOpcodeOverlap
    func._opcodes = opcodes
    func._opversion = version

def declare_opcode_set(func, base_opcode, n_opcodes,
                       op_increment, version=(1,2,3,4,5)):
    """Helper function used for declaring that a function implements
    several opcodes, spaced out at regular interfals in the opcode space."""
    opcodes = [base_opcode+(i*op_increment) for i in range(0, n_opcodes)]
    return declare_opcodes(func, opcodes, version)

def declare_opcode(func, opcode, version=(1,2,3,4,5)):
    """Helper function used for declaring that a functions implements
    a single opcode."""
    return declare_opcodes(func, (opcode,), version)

def append_opcode(func, opcode):
    """Helper function to add one extra opcode to an already declared
    function."""
    opcodes = func._opcodes
    del func._opcodes
    return declare_opcodes(func, opcodes+[opcode], func._opversion)

class ZCpu(object):

    _opcodes = {}

    def __init__(self, zmem, zopdecoder, stackmanager):
        self._memory = zmem
        self._opdecoder = zopdecoder
        self._stackmanager = stackmanager

    def _get_handler(self, opcode):
        opcode_func = self._opcodes.get((opcode, self._memory.version))
        if not opcode_func:
            raise ZCpuIllegalInstruction

        # The following is a hack, based on our policy of only
        # documenting opcodes we implement. If we ever hit an
        # undocumented opcode, we crash with a not implemented
        # error.
        func = getattr(self, opcode_func)
        if func.__doc__ == "":
            raise ZCpuUnimplementedInstruction(func)
        return func

    def _read_variable(self, addr):
        """Return the value of the given variable, which can come from
        the stack, or from a local/global variable.  If it comes from
        the stack, the value is popped from the stack."""
        if addr == 0x0:
            return self._stackmanager.pop_stack()
        elif 0x0 < addr < 0x10:
            return self._stackmanager.get_local_variable(addr - 1)
        else:
            return self._memory.read_global(addr)

    def _write_result(self, result_value, store_addr=None):
        """Write the given result value to the stack or to a
        local/global variable.  Write result_value to the store_addr
        variable, or if None, extract the destination variable from
        the opcode."""
        if store_addr == None:
            result_addr = self._opdecoder.get_store_address()
        else:
            result_addr = store_addr

        if result_addr != None:
            print ">> $%d = %d" % (result_addr, result_value)
            if result_addr == 0x0:
                self._stackmanager.push_stack(result_value)
            elif 0x0 < result_addr < 0x10:
                self._stackmanager.set_local_variable(result_addr - 1,
                                                      result_value)
            else:
                self._memory.write_global(result_addr, result_value)

    def _branch(self, test_result):
        """Retrieve the branch information, and set the instruction
        pointer according to the type of branch and the test_result."""
        branch_cond, branch_offset = self._opdecoder.get_branch_offset()

        if test_result == branch_cond:
            if branch_offset == 0 or branch_offset == 1:
                print ">> Return %d" % branch_offset
                addr = self._stackmanager.finish_routine(branch_offset)
                self._opdecoder.program_counter = addr
            else:
                print ">> Jump +%d" % branch_offset
                self._opdecoder.program_counter += (branch_offset - 2)

    def run(self):
        """The Magic Function that takes little bits and bytes, twirls
        them around, and brings the magic to your screen!"""
        print "Execution started"
        while True:
            try:
                (opcode, operands) = self._opdecoder.get_next_instruction()
                func = self._get_handler(opcode)
                print "<0x%X> (0x%X) %s %s" % (
                    self._opdecoder.program_counter, opcode, func.__name__,
                    ', '.join([str(x) for x in operands]))
                func(*operands)
            except ZCpuUnimplementedInstruction, e:
                print "<0x%X> (0x%X) %s %s ???" % (
                    self._opdecoder.program_counter, opcode,
                    e.args[0].__name__, ', '.join([str(x) for x in operands]))
                break

    ##
    ## Opcode implementation functions start here.
    ##

    ## 2OP opcodes (opcodes 1-127 and 192-223)
    def op_je(self, *args):
        """Branch if the first argument is equal to any of the
        subsequent arguments."""
        self._branch(args[0] in args[1:])

    declare_opcode_set(op_je, 0x01, 4, 0x20)
    append_opcode(op_je, 0xC1)

    def op_jl(self, *args):
        """"""
    declare_opcode_set(op_jl, 0x02, 4, 0x20)
    append_opcode(op_jl, 0xC2)

    def op_jg(self, *args):
        """"""
    declare_opcode_set(op_jg, 0x03, 4, 0x20)
    append_opcode(op_jg, 0xC3)

    def op_dec_chk(self, variable, test_value):
        """Decrement the variable, and branch if the value becomes
        less than test_value."""
        val = self._read_variable(variable)
        val = (val - 1) % 65536
        self._write_result(val, store_addr=variable)
        self._branch(val < test_value)

    declare_opcode_set(op_dec_chk, 0x04, 4, 0x20)
    append_opcode(op_dec_chk, 0xC4)

    def op_inc_chk(self, variable, test_value):
        """Increment the variable, and branch if the value becomes
        greater than the test value."""
        val = self._read_variable(variable)
        val = (val + 1) % 65536
        self._write_result(val, store_addr=variable)
        self._branch(val > test_value)

    declare_opcode_set(op_inc_chk, 0x05, 4, 0x20)
    append_opcode(op_inc_chk, 0xC5)

    def op_jin(self, *args):
        """"""
    declare_opcode_set(op_jin, 0x06, 4, 0x20)
    append_opcode(op_jin, 0xC6)

    def op_test(self, *args):
        """"""
    declare_opcode_set(op_test, 0x07, 4, 0x20)
    append_opcode(op_jin, 0xC7)

    def op_or(self, *args):
        """"""
    declare_opcode_set(op_or, 0x08, 4, 0x20)
    append_opcode(op_or, 0xC8)

    def op_and(self, *args):
        """"""
    declare_opcode_set(op_and, 0x09, 4, 0x20)
    append_opcode(op_and, 0xC9)

    def op_test_attr(self, *args):
        """"""
    declare_opcode_set(op_test_attr, 0x0A, 4, 0x20)
    append_opcode(op_test_attr, 0xCA)

    def op_set_attr(self, *args):
        """"""
    declare_opcode_set(op_set_attr, 0x0B, 4, 0x20)
    append_opcode(op_set_attr, 0xCB)

    def op_clear_attr(self, *args):
        """"""
    declare_opcode_set(op_clear_attr, 0x0C, 4, 0x20)
    append_opcode(op_clear_attr, 0xCC)

    def op_store(self, variable, value):
        """Store the given value to the given variable."""
        self._write_result(value, store_addr=variable)
    declare_opcode_set(op_store, 0x0D, 4, 0x20)
    append_opcode(op_store, 0xCD)

    def op_insert_obj(self, *args):
        """"""
    declare_opcode_set(op_insert_obj, 0x0E, 4, 0x20)
    append_opcode(op_insert_obj, 0xCE)

    def op_loadw(self, base, offset):
        """Store in the given result register the word value at
        (base+2*offset)."""

        val = self._memory.read_word(base + 2*offset)
        self._write_result(val)

    declare_opcode_set(op_loadw, 0x0F, 4, 0x20)
    append_opcode(op_loadw, 0xCF)

    def op_loadb(self, base, offset):
        """Store in the given result register the byte value at
        (base+offset)."""
        val = self._memory[base+offset]
        self._write_result(val)

    declare_opcode_set(op_loadb, 0x10, 4, 0x20)
    append_opcode(op_loadb, 0xD0)

    def op_get_prop(self, *args):
        """"""
    declare_opcode_set(op_get_prop, 0x11, 4, 0x20)
    append_opcode(op_get_prop, 0xD1)

    def op_get_prop_addr(self, *args):
        """"""
    declare_opcode_set(op_get_prop_addr, 0x12, 4, 0x20)
    append_opcode(op_get_prop_addr, 0xD2)

    def op_get_next_prop(self, *args):
        """"""
    declare_opcode_set(op_get_next_prop, 0x13, 4, 0x20)
    append_opcode(op_get_next_prop, 0xD3)

    def op_add(self, *args):
        """Signed 16-bit addition."""
        self._write_result(sum(args) % 65536) # 2**16 - overflow limit
    declare_opcode_set(op_add, 0x14, 4, 0x20)
    append_opcode(op_add, 0xD4)

    def op_sub(self, *args):
        """"""
    declare_opcode_set(op_sub, 0x15, 4, 0x20)
    append_opcode(op_sub, 0xD5)

    def op_mul(self, *args):
        """Signed 16-bit multiplication."""
        result = reduce(lambda x,y: x*y, args) % 65536
        self._write_result(result)
    declare_opcode_set(op_mul, 0x16, 4, 0x20)
    append_opcode(op_mul, 0xD6)

    def op_div(self, *args):
        """"""
    declare_opcode_set(op_div, 0x17, 4, 0x20)
    append_opcode(op_div, 0xD7)

    def op_mod(self, *args):
        """"""
    declare_opcode_set(op_mod, 0x18, 4, 0x20)
    append_opcode(op_mod, 0xD8)

    def op_call_2s(self, *args):
        """"""
    declare_opcode_set(op_call_2s, 0x19, 4, 0x20, version=(4,5))
    append_opcode(op_call_2s, 0xD9)

    def op_call_2n(self, *args):
        """"""
    declare_opcode_set(op_call_2n, 0x1A, 4, 0x20, version=(5,))
    append_opcode(op_call_2n, 0xDA)

    def op_set_colour(self, *args):
        """"""
    declare_opcode_set(op_set_colour, 0x1B, 4, 0x20, version=(5,))
    append_opcode(op_set_colour, 0xDB)

    def op_throw(self, *args):
        """"""
    declare_opcode_set(op_throw, 0x1C, 4, 0x20, version=(5,))
    append_opcode(op_throw, 0xDC)

    ## 1OP opcodes (opcodes 128-175)

    def op_jz(self, val):
        """Branch if the val is zero."""
        self._branch(val == 0)
    declare_opcode_set(op_jz, 0x80, 3, 0x10)

    def op_get_sibling(self, *args):
        """"""
    declare_opcode_set(op_get_sibling, 0x81, 3, 0x10)

    def op_get_child(self, *args):
        """"""
    declare_opcode_set(op_get_child, 0x82, 3, 0x10)

    def op_get_parent(self, *args):
        """"""
    declare_opcode_set(op_get_parent, 0x83, 3, 0x10)

    def op_get_prop_len(self, *args):
        """"""
    declare_opcode_set(op_get_prop_len, 0x84, 3, 0x10)

    def op_inc(self, *args):
        """"""
    declare_opcode_set(op_inc, 0x85, 3, 0x10)

    def op_dec(self, *args):
        """"""
    declare_opcode_set(op_dec, 0x86, 3, 0x10)

    def op_print_addr(self, *args):
        """"""
    declare_opcode_set(op_print_addr, 0x87, 3, 0x10)

    def op_call_1s(self, *args):
        """"""
    declare_opcode_set(op_call_1s, 0x88, 3, 0x10, version=(4,5))

    def op_remove_obj(self, *args):
        """"""
    declare_opcode_set(op_remove_obj, 0x89, 3, 0x10)

    def op_print_obj(self, *args):
        """"""
    declare_opcode_set(op_print_obj, 0x8A, 3, 0x10)

    def op_ret(self, *args):
        """"""
    declare_opcode_set(op_ret, 0x8B, 3, 0x10)

    def op_jump(self, *args):
        """Jump unconditionally to the given branch offset.  This
        opcode does not follow the usual branch decision algorithm,
        and so we do not call the _branch method to dispatch the call."""
        cond, offset = self._opdecoder.get_branch_offset()
        self._opdecoder.program_counter += (offset - 2)
    declare_opcode_set(op_jump, 0x8C, 3, 0x10)

    def op_print_paddr(self, *args):
        """"""
    declare_opcode_set(op_print_paddr, 0x8D, 3, 0x10)

    def op_load(self, *args):
        """"""
    declare_opcode_set(op_load, 0x8E, 3, 0x10)

    def op_not(self, *args):
        """"""
    declare_opcode_set(op_not, 0x8F, 3, 0x10, version=(1,2,3,4))

    def op_call_1n(self, routine_addr):
        """Call the given routine, and discard the return value."""
        addr = self._memory.packed_address(routine_addr)
        current_addr = self._opdecoder.program_counter
        new_addr = self._stackmanager.start_routine(addr, None,
                                                    current_addr, [])
        self._opdecoder.program_counter = new_addr

    declare_opcode_set(op_call_1n, 0x8F, 3, 0x10, version=(5,))

    ## 0OP opcodes (opcodes 176-191)

    def op_rtrue(self, *args):
        """"""
    declare_opcode(op_rtrue, 0xB0)

    def op_rfalse(self, *args):
        """"""
    declare_opcode(op_rfalse, 0xB1)

    def op_print(self, *args):
        """"""
    declare_opcode(op_print, 0xB2)

    def op_print_ret(self, *args):
        """"""
    declare_opcode(op_print_ret, 0xB3)

    def op_nop(self, *args):
        """"""
    declare_opcode(op_nop, 0xB4)

    def op_save(self, *args):
        """"""
    declare_opcode(op_save, 0xB5, version=(1,2,3))

    def op_save_v4(self, *args):
        """"""
    declare_opcode(op_save_v4, 0xB5, version=(4,))

    def op_restore(self, *args):
        """"""
    declare_opcode(op_restore, 0xB6, version=(1,2,3))

    def op_restore_v4(self, *args):
        """"""
    declare_opcode(op_restore_v4, 0xB6, version=(4,))

    def op_restart(self, *args):
        """"""
    declare_opcode(op_restart, 0xB7)

    def op_ret_popped(self, *args):
        """"""
    declare_opcode(op_ret_popped, 0xB8)

    def op_pop(self, *args):
        """"""
    declare_opcode(op_pop, 0xB9, version=(1,2,3,4))

    def op_catch(self, *args):
        """"""
    declare_opcode(op_catch, 0xB9, version=(5,))

    def op_quit(self, *args):
        """"""
    declare_opcode(op_quit, 0xBA)

    def op_new_line(self, *args):
        """"""
    declare_opcode(op_new_line, 0xBB)

    def op_show_status(self, *args):
        """"""
    declare_opcode(op_show_status, 0xBC, version=(3,))

    def op_verify(self, *args):
        """"""
    declare_opcode(op_verify, 0xBD)

    def op_piracy(self, *args):
        """"""
    declare_opcode(op_piracy, 0xBF)

    ## VAR opcodes (opcodes 224-255)

    # call in v1-3, call_vs in v4-5
    def op_call(self, routine_addr, *args):
        """Call the routine r1, passing it any of r2, r3, r4 if defined."""
        addr = self._memory.packed_address(routine_addr)
        return_addr = self._opdecoder.get_store_address()
        current_addr = self._opdecoder.program_counter
        new_addr = self._stackmanager.start_routine(addr,
                                                    return_addr,
                                                    current_addr,
                                                    args)
        self._opdecoder.program_counter = new_addr
    declare_opcode(op_call, 0xE0)

    def op_storew(self, *args):
        """"""
    declare_opcode(op_storew, 0xE1)

    def op_storeb(self, *args):
        """"""
    declare_opcode(op_storeb, 0xE2)

    def op_put_prop(self, *args):
        """"""
    declare_opcode(op_put_prop, 0xE3)

    def op_sread(self, *args):
        """Not implemented yet, but documented so that the detection
        code will be foiled."""
    declare_opcode(op_sread, 0xE4, version=(1,2,3))

    def op_sread_v4(self, *args):
        """"""
    declare_opcode(op_sread_v4, 0xE4, version=(4,))

    def op_aread(self, *args):
        """"""
    declare_opcode(op_aread, 0xE4, version=(5,))

    def op_print_char(self, *args):
        """"""
    declare_opcode(op_print_char, 0xE5)

    def op_print_num(self, *args):
        """"""
    declare_opcode(op_print_num, 0xE6)

    def op_random(self, *args):
        """"""
    declare_opcode(op_random, 0xE7)

    def op_push(self, *args):
        """"""
    declare_opcode(op_push, 0xE8)

    def op_pull(self, *args):
        """"""
    declare_opcode(op_pull, 0xE9)

    def op_split_window(self, *args):
        """"""
    declare_opcode(op_split_window, 0xEA, version=(3,4,5))

    def op_set_window(self, *args):
        """"""
    declare_opcode(op_set_window, 0xEB, version=(3,4,5))

    def op_call_vs2(self, *args):
        """"""
    declare_opcode(op_call_vs2, 0xEC, version=(4,5))

    def op_erase_window(self, *args):
        """"""
    declare_opcode(op_erase_window, 0xED, version=(4,5))

    def op_erase_line(self, *args):
        """"""
    declare_opcode(op_erase_line, 0xEE, version=(4,5))

    def op_set_cursor(self, *args):
        """"""
    declare_opcode(op_set_cursor, 0xEF, version=(4,5))

    def op_get_cursor(self, *args):
        """"""
    declare_opcode(op_get_cursor, 0xF0, version=(4,5))

    def op_set_text_style(self, *args):
        """"""
    declare_opcode(op_set_text_style, 0xF1, version=(4,5))

    def op_buffer_mode(self, *args):
        """"""
    declare_opcode(op_buffer_mode, 0xF2, version=(4,5))

    def op_output_stream(self, *args):
        """"""
    declare_opcode(op_output_stream, 0xF3, version=(3,4))

    def op_output_stream_v5(self, *args):
        """"""
    declare_opcode(op_output_stream_v5, 0xF3, version=(5,))

    def op_input_stream(self, *args):
        """"""
    declare_opcode(op_input_stream, 0xF4, version=(3,4,5))

    # This one may have been used prematurely in v3 stories. Keep an
    # eye out for it if we ever get bug reports.
    def op_sound_effect(self, *args):
        """"""
    declare_opcode(op_sound_effect, 0xF5, version=(5,))

    def op_read_char(self, *args):
        """"""
    declare_opcode(op_read_char, 0xF6, version=(4,5))

    def op_scan_table(self, *args):
        """"""
    declare_opcode(op_scan_table, 0xF7, version=(4,5))

    def op_not_v5(self, *args):
        """"""
    declare_opcode(op_not_v5, 0xF8, version=(5,))

    def op_call_vn(self, *args):
        """"""
    declare_opcode(op_call_vn, 0xF9, version=(5,))

    def op_call_vn2(self, *args):
        """"""
    declare_opcode(op_call_vn2, 0xFA, version=(5,))

    def op_tokenize(self, *args):
        """"""
    declare_opcode(op_tokenize, 0xFB, version=(5,))

    def op_encode_text(self, *args):
        """"""
    declare_opcode(op_encode_text, 0xFC, version=(5,))

    def op_copy_table(self, *args):
        """"""
    declare_opcode(op_copy_table, 0xFD, version=(5,))

    def op_print_table(self, *args):
        """"""
    declare_opcode(op_print_table, 0xFE, version=(5,))

    def op_check_arg_count(self, *args):
        """"""
    declare_opcode(op_check_arg_count, 0xFF, version=(5,))

    ## EXT opcodes (opcodes 256-284)

    def op_save(self, *args):
        """"""
    declare_opcode(op_save, 0x100, version=(5,))

    def op_restore(self, *args):
        """"""
    declare_opcode(op_restore, 0x101, version=(5,))

    def op_log_shift(self, *args):
        """"""
    declare_opcode(op_log_shift, 0x102, version=(5,))

    def op_art_shift(self, *args):
        """"""
    declare_opcode(op_art_shift, 0x103, version=(5,))

    def op_set_font(self, *args):
        """"""
    declare_opcode(op_set_font, 0x104, version=(5,))

    def op_save_undo(self, *args):
        """"""
    declare_opcode(op_save_undo, 0x109, version=(5,))

    def op_restore_undo(self, *args):
        """"""
    declare_opcode(op_restore_undo, 0x10A, version=(5,))

    def op_print_unicode(self, *args):
        """"""
    declare_opcode(op_print_unicode, 0x10B, version=(5,))

    def op_check_unicode(self, *args):
        """"""
    declare_opcode(op_check_unicode, 0x10C, version=(5,))


    # This is the "automagic" opcode handler registration system.
    # After each function that is an opcode handler, we assign the
    # function object an _opcode attribute, giving the numeric opcode
    # the function implements.
    #
    # Then, the following code iterates back over all items in the
    # class, and registers all objects with that attribute in the
    # _opcodes dictionary.
    #
    # Then, at runtime, the _get_handler method can be invoked to
    # retrieve the function implementing a given opcode.  Pretty cool
    # voodoo if you ask me.
    for k,v in vars().items():
        if hasattr(v, "_opcodes"):
            for opc in v._opcodes:
                for ver in v._opversion:
                    opkey = (opc, ver)

                    if opkey in _opcodes.keys():
                        print "Opcode key",opkey,"already defined"
                        raise ZCpuOpcodeOverlap

                    _opcodes[opkey] = k
