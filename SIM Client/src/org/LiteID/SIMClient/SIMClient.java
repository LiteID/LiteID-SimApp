package org.LiteID.SIMClient;

import javacard.framework.APDU;
import javacard.framework.Applet;
import javacard.framework.ISOException;

import sim.toolkit.EnvelopeHandler;
import sim.toolkit.ProactiveHandler;
import sim.toolkit.ToolkitConstants;
import sim.toolkit.ToolkitException;
import sim.toolkit.ToolkitInterface;
import sim.toolkit.ToolkitRegistry;

public class SIMClient extends Applet implements ToolkitInterface, ToolkitConstants {
	private byte addMenuItem;
	
	static byte[] welcomeMsg = new byte[] { 'W', 'e', 'l', 'c', 'o', 'm', 'e', ' ', 't', 'o', ' ', 'L', 'i', 't', 'e', 'I', 'D'};
	
	static byte[] menuItemText = new byte[] { 'A', 'd', 'd', ' ', 'i', 't', 'e', 'm'};
	
	private SIMClient() {
		ToolkitRegistry reg = ToolkitRegistry.getEntry();
		addMenuItem = reg.initMenuEntry(menuItemText, (short)0, (short)menuItemText.length,
				PRO_CMD_SELECT_ITEM, false, (byte)0, (short)0);
	}

	public static void install(byte[] bArray, short bOffset, byte bLength) {
		SIMClient applet = new SIMClient();
		applet.register();
	}

	public void process(APDU arg0) throws ISOException {
		if (selectingApplet())
			return;
	}

	public void processToolkit(byte event) throws ToolkitException {
		EnvelopeHandler envHdlr = EnvelopeHandler.getTheHandler();

		if (event == EVENT_MENU_SELECTION) {
			byte selectedItemId = envHdlr.getItemIdentifier();

			if (selectedItemId == addMenuItem) {
				showAdd();
			}
		}
	}
	
	private void showAdd() {
		ProactiveHandler proHdlr = ProactiveHandler.getTheHandler();
		proHdlr.initDisplayText((byte)0, DCS_8_BIT_DATA, welcomeMsg, (short)0, 
				(short)(welcomeMsg.length));
		proHdlr.send();
		return;
	}
}